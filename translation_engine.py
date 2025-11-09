from typing import Dict, List, Optional, Tuple
from sqlalchemy.orm import Session
from database import Project, Chapter, GlossaryEntry, TranslationCache, APIConfig, CostTracking
from ai_providers import AIProviderFactory
from cost_tracking import CostTracker
import hashlib
import re
from datetime import datetime


class TranslationEngine:
    """Core translation engine with memory and consistency features"""
    
    def __init__(self, db: Session):
        self.db = db
        self.cost_tracker = CostTracker()
    
    def _get_text_hash(self, text: str) -> str:
        """Generate hash for text caching"""
        return hashlib.sha256(text.encode()).hexdigest()
    
    def _extract_potential_names(self, text: str) -> List[str]:
        """Extract potential character names and proper nouns"""
        # Look for capitalized words (potential names)
        pattern = r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b'
        names = re.findall(pattern, text)
        return list(set(names))
    
    def _get_project_glossary(self, project_id: int) -> Dict[str, str]:
        """Get all glossary entries for a project"""
        entries = self.db.query(GlossaryEntry).filter(
            GlossaryEntry.project_id == project_id
        ).all()
        
        return {entry.original_term: entry.translated_term for entry in entries}
    
    def _update_glossary(self, project_id: int, original_term: str, 
                        translated_term: str, term_type: str = "general"):
        """Add or update glossary entry"""
        entry = self.db.query(GlossaryEntry).filter(
            GlossaryEntry.project_id == project_id,
            GlossaryEntry.original_term == original_term
        ).first()
        
        if entry:
            entry.usage_count += 1
            entry.updated_at = datetime.utcnow()
        else:
            entry = GlossaryEntry(
                project_id=project_id,
                original_term=original_term,
                translated_term=translated_term,
                term_type=term_type,
                usage_count=1
            )
            self.db.add(entry)
        
        self.db.commit()
    
    def _add_terms_to_glossary(self, project_id: int, terms_dict: dict):
        """Add extracted terms to glossary automatically"""
        term_type_map = {
            'character': 'character',
            'location': 'location',
            'skill': 'skill',
            'item': 'item',
            'organization': 'general'
        }
        
        added_count = 0
        
        for term_type, terms_list in terms_dict.items():
            if not isinstance(terms_list, list):
                continue
                
            glossary_type = term_type_map.get(term_type, 'general')
            
            for term in terms_list:
                if isinstance(term, dict) and 'original' in term and 'translation' in term:
                    original = term['original'].strip()
                    translation = term['translation'].strip()
                    
                    if original and translation:
                        # Check if term already exists
                        existing = self.db.query(GlossaryEntry).filter(
                            GlossaryEntry.project_id == project_id,
                            GlossaryEntry.original_term == original
                        ).first()
                        
                        if not existing:
                            entry = GlossaryEntry(
                                project_id=project_id,
                                original_term=original,
                                translated_term=translation,
                                term_type=glossary_type,
                                usage_count=1,
                                confirmed=False  # Auto-added terms are unconfirmed
                            )
                            self.db.add(entry)
                            added_count += 1
        
        if added_count > 0:
            self.db.commit()
            print(f"✅ Auto-added {added_count} terms to glossary")
        
        return added_count
    
    def _check_cache(self, text: str, project_id: int, 
                    source_lang: str, target_lang: str) -> Optional[str]:
        """Check if translation exists in cache"""
        text_hash = self._get_text_hash(text)
        
        cached = self.db.query(TranslationCache).filter(
            TranslationCache.source_text_hash == text_hash,
            TranslationCache.project_id == project_id,
            TranslationCache.source_lang == source_lang,
            TranslationCache.target_lang == target_lang
        ).first()
        
        if cached:
            return cached.translated_text
        return None
    
    def _save_to_cache(self, text: str, translated_text: str, 
                      project_id: int, source_lang: str, 
                      target_lang: str, ai_provider: str):
        """Save translation to cache"""
        text_hash = self._get_text_hash(text)
        
        cache_entry = TranslationCache(
            project_id=project_id,
            source_text_hash=text_hash,
            source_text=text,
            translated_text=translated_text,
            source_lang=source_lang,
            target_lang=target_lang,
            ai_provider=ai_provider
        )
        
        self.db.add(cache_entry)
        self.db.commit()
    
    def _split_into_chunks(self, text: str, max_chunk_size: int = 3000) -> List[str]:
        """Split text into manageable chunks for translation"""
        # Split by paragraphs first
        paragraphs = text.split('\n\n')
        chunks = []
        current_chunk = ""
        
        for para in paragraphs:
            if len(current_chunk) + len(para) < max_chunk_size:
                current_chunk += para + "\n\n"
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = para + "\n\n"
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    async def translate_chapter(self, chapter_id: int, 
                               extract_terms: bool = True) -> Dict:
        """Translate a chapter with memory and consistency"""
        
        # Get chapter and project
        chapter = self.db.query(Chapter).filter(Chapter.id == chapter_id).first()
        if not chapter:
            raise ValueError("Chapter not found")
        
        project = self.db.query(Project).filter(Project.id == chapter.project_id).first()
        if not project:
            raise ValueError("Project not found")
        
        # Get AI configuration
        api_config = self.db.query(APIConfig).filter(
            APIConfig.provider_name == project.ai_provider,
            APIConfig.enabled == True
        ).first()
        
        if not api_config or not api_config.api_key:
            raise ValueError(f"AI provider '{project.ai_provider}' not configured or disabled")
        
        # Update chapter status
        chapter.status = "processing"
        self.db.commit()
        
        try:
            # Get glossary
            glossary = self._get_project_glossary(project.id)
            
            # Get previous chapter for context
            prev_chapter = self.db.query(Chapter).filter(
                Chapter.project_id == project.id,
                Chapter.chapter_number < chapter.chapter_number
            ).order_by(Chapter.chapter_number.desc()).first()
            
            context = None
            if prev_chapter and prev_chapter.translated_text:
                # Get last paragraph as context
                context_paragraphs = prev_chapter.translated_text.split('\n\n')
                if context_paragraphs:
                    context = context_paragraphs[-1][:500]  # Last 500 chars
            
            # Create AI provider
            provider = AIProviderFactory.create_provider(
                provider_name=api_config.provider_name,
                api_key=api_config.api_key,
                model=api_config.model or project.ai_model,
                temperature=api_config.temperature,
                max_tokens=api_config.max_tokens
            )
            
            # Check cache first
            cached_translation = self._check_cache(
                chapter.original_text,
                project.id,
                project.source_language,
                project.target_language
            )
            
            chunks = []  # Initialize chunks variable
            
            if cached_translation:
                translated_text = cached_translation
                from_cache = True
            else:
                # Split text into chunks if needed
                chunks = self._split_into_chunks(chapter.original_text)
                translated_chunks = []
                
                for i, chunk in enumerate(chunks):
                    # Use context only for first chunk
                    chunk_context = context if i == 0 else None
                    
                    # Extract terms from first chunk only to avoid redundancy
                    should_extract = extract_terms and i == 0
                    
                    result = await provider.translate(
                        text=chunk,
                        source_lang=project.source_language,
                        target_lang=project.target_language,
                        glossary=glossary,
                        context=chunk_context,
                        extract_terms=should_extract
                    )
                    
                    # Handle both dict and string responses
                    if isinstance(result, dict):
                        translated_chunks.append(result.get('translation', result.get('text', chunk)))
                        
                        # Process extracted terms
                        if should_extract and result.get('terms'):
                            extracted_terms = result['terms']
                            self._add_terms_to_glossary(project.id, extracted_terms)
                    else:
                        translated_chunks.append(result)
                
                translated_text = "\n\n".join(translated_chunks)
                from_cache = False
                
                # Save to cache
                self._save_to_cache(
                    chapter.original_text,
                    translated_text,
                    project.id,
                    project.source_language,
                    project.target_language,
                    api_config.provider_name
                )
            
            # Extract and update terms if requested
            new_terms = []
            if extract_terms and not from_cache:
                potential_names = self._extract_potential_names(chapter.original_text)
                # Here you could use AI to identify which translations in the 
                # translated text correspond to these names
                # For now, we'll just note them
                new_terms = potential_names
            
            # Track costs if not from cache
            cost_data = {}
            if not from_cache:
                input_tokens = self.cost_tracker.count_tokens(chapter.original_text)
                output_tokens = self.cost_tracker.count_tokens(translated_text)
                cost_data = self.cost_tracker.estimate_cost(
                    api_config.provider_name,
                    api_config.model or project.ai_model or "",
                    input_tokens,
                    output_tokens
                )
                
                # Save cost tracking
                cost_record = CostTracking(
                    project_id=project.id,
                    chapter_id=chapter.id,
                    ai_provider=api_config.provider_name,
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    total_tokens=input_tokens + output_tokens,
                    estimated_cost=cost_data['total_cost']
                )
                self.db.add(cost_record)
            
            # Update chapter
            chapter.translated_text = translated_text
            chapter.status = "completed"
            chapter.translation_stats = {
                "original_length": len(chapter.original_text),
                "translated_length": len(translated_text),
                "chunks_processed": len(chunks) if not from_cache else 1,
                "from_cache": from_cache,
                "new_terms_found": len(new_terms),
                "glossary_size": len(glossary),
                "translated_at": datetime.utcnow().isoformat(),
                "cost": cost_data if cost_data else None
            }
            
            self.db.commit()
            
            return {
                "success": True,
                "chapter_id": chapter.id,
                "translated_text": translated_text,
                "stats": chapter.translation_stats,
                "new_terms": new_terms
            }
            
        except Exception as e:
            chapter.status = "error"
            chapter.translation_stats = {
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
            self.db.commit()
            
            return {
                "success": False,
                "chapter_id": chapter.id,
                "error": str(e)
            }
    
    def get_translation_statistics(self, project_id: int) -> Dict:
        """Get translation statistics for a project"""
        project = self.db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise ValueError("Project not found")
        
        chapters = self.db.query(Chapter).filter(Chapter.project_id == project_id).all()
        glossary_count = self.db.query(GlossaryEntry).filter(
            GlossaryEntry.project_id == project_id
        ).count()
        
        total_chapters = len(chapters)
        completed_chapters = sum(1 for c in chapters if c.status == "completed")
        total_words = sum(len(c.original_text.split()) for c in chapters)
        translated_words = sum(
            len(c.translated_text.split()) if c.translated_text else 0 
            for c in chapters
        )
        
        return {
            "project_name": project.name,
            "total_chapters": total_chapters,
            "completed_chapters": completed_chapters,
            "pending_chapters": sum(1 for c in chapters if c.status == "pending"),
            "error_chapters": sum(1 for c in chapters if c.status == "error"),
            "glossary_terms": glossary_count,
            "total_words": total_words,
            "translated_words": translated_words,
            "completion_rate": (completed_chapters / total_chapters * 100) if total_chapters > 0 else 0
        }

