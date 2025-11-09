"""
Advanced Glossary Service - Enhanced term management
"""
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from database import GlossaryEntry
import re
from difflib import SequenceMatcher


class GlossaryService:
    """Advanced glossary management service"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def search_terms(self, project_id: int, query: str, term_type: str = None,
                    confirmed_only: bool = False) -> List[GlossaryEntry]:
        """Search glossary terms with filters"""
        
        search_query = self.db.query(GlossaryEntry).filter(
            GlossaryEntry.project_id == project_id
        )
        
        # Text search
        if query:
            search_query = search_query.filter(
                or_(
                    GlossaryEntry.original_term.ilike(f'%{query}%'),
                    GlossaryEntry.translated_term.ilike(f'%{query}%'),
                    GlossaryEntry.context.ilike(f'%{query}%')
                )
            )
        
        # Type filter
        if term_type:
            search_query = search_query.filter(GlossaryEntry.term_type == term_type)
        
        # Confirmed filter
        if confirmed_only:
            search_query = search_query.filter(GlossaryEntry.confirmed == True)
        
        return search_query.order_by(GlossaryEntry.usage_count.desc()).all()
    
    def find_similar_terms(self, project_id: int, term: str, threshold: float = 0.7) -> List[Dict]:
        """Find similar terms in glossary (for consistency checking)"""
        
        all_terms = self.db.query(GlossaryEntry).filter(
            GlossaryEntry.project_id == project_id
        ).all()
        
        similar = []
        
        for entry in all_terms:
            # Calculate similarity
            similarity = SequenceMatcher(None, term.lower(), entry.original_term.lower()).ratio()
            
            if similarity >= threshold and term.lower() != entry.original_term.lower():
                similar.append({
                    'id': entry.id,
                    'original_term': entry.original_term,
                    'translated_term': entry.translated_term,
                    'similarity': round(similarity, 2),
                    'term_type': entry.term_type
                })
        
        # Sort by similarity
        similar.sort(key=lambda x: x['similarity'], reverse=True)
        
        return similar[:5]  # Top 5
    
    def get_statistics(self, project_id: int) -> Dict:
        """Get comprehensive glossary statistics"""
        
        entries = self.db.query(GlossaryEntry).filter(
            GlossaryEntry.project_id == project_id
        ).all()
        
        if not entries:
            return {
                'total_terms': 0,
                'by_type': {},
                'by_status': {},
                'most_used': [],
                'recently_added': []
            }
        
        # Count by type
        by_type = {}
        by_status = {'confirmed': 0, 'unconfirmed': 0}
        
        for entry in entries:
            # By type
            term_type = entry.term_type
            by_type[term_type] = by_type.get(term_type, 0) + 1
            
            # By status
            if entry.confirmed:
                by_status['confirmed'] += 1
            else:
                by_status['unconfirmed'] += 1
        
        # Most used
        most_used = sorted(entries, key=lambda x: x.usage_count, reverse=True)[:10]
        
        # Recently added
        recently_added = sorted(entries, key=lambda x: x.created_at, reverse=True)[:10]
        
        return {
            'total_terms': len(entries),
            'by_type': by_type,
            'by_status': by_status,
            'most_used': [
                {
                    'original': e.original_term,
                    'translated': e.translated_term,
                    'count': e.usage_count,
                    'type': e.term_type
                }
                for e in most_used
            ],
            'recently_added': [
                {
                    'original': e.original_term,
                    'translated': e.translated_term,
                    'type': e.term_type,
                    'confirmed': e.confirmed
                }
                for e in recently_added
            ]
        }
    
    def bulk_confirm(self, project_id: int, term_ids: List[int]) -> int:
        """Confirm multiple terms at once"""
        
        updated = self.db.query(GlossaryEntry).filter(
            GlossaryEntry.project_id == project_id,
            GlossaryEntry.id.in_(term_ids)
        ).update({'confirmed': True}, synchronize_session=False)
        
        self.db.commit()
        
        return updated
    
    def bulk_delete(self, project_id: int, term_ids: List[int]) -> int:
        """Delete multiple terms at once"""
        
        deleted = self.db.query(GlossaryEntry).filter(
            GlossaryEntry.project_id == project_id,
            GlossaryEntry.id.in_(term_ids)
        ).delete(synchronize_session=False)
        
        self.db.commit()
        
        return deleted
    
    def bulk_update_type(self, project_id: int, term_ids: List[int], new_type: str) -> int:
        """Update type for multiple terms"""
        
        updated = self.db.query(GlossaryEntry).filter(
            GlossaryEntry.project_id == project_id,
            GlossaryEntry.id.in_(term_ids)
        ).update({'term_type': new_type}, synchronize_session=False)
        
        self.db.commit()
        
        return updated
    
    def merge_duplicates(self, project_id: int) -> int:
        """Merge duplicate terms (same original_term)"""
        
        # Find duplicates
        duplicates = self.db.query(
            GlossaryEntry.original_term,
            func.count(GlossaryEntry.id).label('count')
        ).filter(
            GlossaryEntry.project_id == project_id
        ).group_by(
            GlossaryEntry.original_term
        ).having(
            func.count(GlossaryEntry.id) > 1
        ).all()
        
        merged_count = 0
        
        for original_term, count in duplicates:
            # Get all entries for this term
            entries = self.db.query(GlossaryEntry).filter(
                GlossaryEntry.project_id == project_id,
                GlossaryEntry.original_term == original_term
            ).order_by(
                GlossaryEntry.confirmed.desc(),
                GlossaryEntry.usage_count.desc()
            ).all()
            
            if len(entries) <= 1:
                continue
            
            # Keep first (most used/confirmed), merge others
            keep = entries[0]
            duplicates_to_remove = entries[1:]
            
            for dup in duplicates_to_remove:
                keep.usage_count += dup.usage_count
                if not keep.confirmed and dup.confirmed:
                    keep.confirmed = True
                self.db.delete(dup)
                merged_count += 1
        
        self.db.commit()
        
        return merged_count
    
    def suggest_translations(self, original_term: str, target_lang: str = "tr") -> List[str]:
        """Suggest possible translations based on patterns"""
        
        # Simple pattern-based suggestions
        suggestions = []
        
        # If it's a compound word
        if ' ' in original_term:
            words = original_term.split()
            # Suggest keeping proper nouns
            if all(w[0].isupper() for w in words):
                suggestions.append(original_term)  # Keep as-is
        
        # Common patterns
        patterns = {
            'Guild': 'Lonca',
            'Hunter': 'Avcı',
            'King': 'Kral',
            'Queen': 'Kraliçe',
            'Monarch': 'Hükümdar',
            'Shadow': 'Gölge',
            'Dark': 'Karanlık',
            'Light': 'Işık',
            'Dragon': 'Ejderha',
            'Sword': 'Kılıç',
            'Magic': 'Büyü',
            'Skill': 'Yetenek',
            'Level': 'Seviye',
            'Dungeon': 'Zindan'
        }
        
        for eng, tr in patterns.items():
            if eng in original_term:
                suggestion = original_term.replace(eng, tr)
                if suggestion not in suggestions:
                    suggestions.append(suggestion)
        
        return suggestions[:3]  # Top 3 suggestions
    
    def analyze_consistency(self, project_id: int) -> Dict:
        """Analyze translation consistency"""
        
        entries = self.db.query(GlossaryEntry).filter(
            GlossaryEntry.project_id == project_id
        ).all()
        
        issues = []
        
        # Find potential issues
        for i, entry in enumerate(entries):
            # Check for similar original terms with different translations
            for other in entries[i+1:]:
                similarity = SequenceMatcher(
                    None,
                    entry.original_term.lower(),
                    other.original_term.lower()
                ).ratio()
                
                if similarity > 0.8 and entry.translated_term != other.translated_term:
                    issues.append({
                        'type': 'similar_terms_different_translation',
                        'term1': entry.original_term,
                        'translation1': entry.translated_term,
                        'term2': other.original_term,
                        'translation2': other.translated_term,
                        'similarity': round(similarity, 2)
                    })
        
        return {
            'total_entries': len(entries),
            'consistency_issues': issues[:10],  # Top 10 issues
            'issue_count': len(issues)
        }

