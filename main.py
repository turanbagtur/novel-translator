from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
import os

from database import (get_db, init_db, Project, Chapter, GlossaryEntry, APIConfig, 
                      TranslationJob, CostTracking, ChapterRevision, ProjectBackup, UserSettings)
from translation_engine import TranslationEngine
from ai_providers import AIProviderFactory
from config import settings
from contextlib import asynccontextmanager
from export_service import ExportService
from cost_tracking import CostTracker
from batch_translation import BatchTranslationService
from backup_service import BackupService
from glossary_service import GlossaryService
import asyncio
import pandas as pd
from io import BytesIO

# Initialize database on startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    init_db()
    print(f"🚀 {settings.APP_NAME} v{settings.APP_VERSION} - Server started successfully!")
    print(f"📍 Open: http://localhost:8000")
    yield
    # Shutdown (cleanup if needed)
    print("👋 Shutting down...")

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Advanced Novel Translation System with AI-powered consistency",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for API
class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    source_language: str = "en"
    target_language: str = "tr"
    ai_provider: str = "gemini"
    ai_model: Optional[str] = None

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    source_language: Optional[str] = None
    target_language: Optional[str] = None
    ai_provider: Optional[str] = None
    ai_model: Optional[str] = None

class ChapterCreate(BaseModel):
    chapter_number: int
    title: Optional[str] = None
    original_text: str

class ChapterUpdate(BaseModel):
    title: Optional[str] = None
    original_text: Optional[str] = None
    translated_text: Optional[str] = None

class GlossaryCreate(BaseModel):
    original_term: str
    translated_term: str
    term_type: str = "general"
    context: Optional[str] = None

class APIConfigCreate(BaseModel):
    provider_name: str
    api_key: Optional[str] = None
    api_url: Optional[str] = None
    model: Optional[str] = None
    max_tokens: int = 4000
    temperature: float = 0.7
    enabled: bool = True

class TranslationRequest(BaseModel):
    chapter_id: int
    extract_terms: bool = True

# ============= API ENDPOINTS =============

# Root endpoint
@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main web interface"""
    return FileResponse("static/index.html")

# ============= PROJECT ENDPOINTS =============

@app.get("/api/projects")
async def list_projects(db: Session = Depends(get_db)):
    """List all projects"""
    projects = db.query(Project).all()
    return [
        {
            "id": p.id,
            "name": p.name,
            "description": p.description,
            "source_language": p.source_language,
            "target_language": p.target_language,
            "ai_provider": p.ai_provider,
            "created_at": p.created_at.isoformat(),
            "chapter_count": len(p.chapters)
        }
        for p in projects
    ]

@app.post("/api/projects")
async def create_project(project: ProjectCreate, db: Session = Depends(get_db)):
    """Create a new project"""
    new_project = Project(
        name=project.name,
        description=project.description,
        source_language=project.source_language,
        target_language=project.target_language,
        ai_provider=project.ai_provider,
        ai_model=project.ai_model
    )
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    
    return {"id": new_project.id, "message": "Project created successfully"}

@app.get("/api/projects/{project_id}")
async def get_project(project_id: int, db: Session = Depends(get_db)):
    """Get project details"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return {
        "id": project.id,
        "name": project.name,
        "description": project.description,
        "source_language": project.source_language,
        "target_language": project.target_language,
        "ai_provider": project.ai_provider,
        "ai_model": project.ai_model,
        "created_at": project.created_at.isoformat(),
        "updated_at": project.updated_at.isoformat(),
        "chapters": [
            {
                "id": c.id,
                "chapter_number": c.chapter_number,
                "title": c.title,
                "status": c.status,
                "created_at": c.created_at.isoformat()
            }
            for c in sorted(project.chapters, key=lambda x: x.chapter_number)
        ]
    }

@app.put("/api/projects/{project_id}")
async def update_project(project_id: int, project: ProjectUpdate, db: Session = Depends(get_db)):
    """Update project"""
    db_project = db.query(Project).filter(Project.id == project_id).first()
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if project.name:
        db_project.name = project.name
    if project.description is not None:
        db_project.description = project.description
    if project.source_language:
        db_project.source_language = project.source_language
    if project.target_language:
        db_project.target_language = project.target_language
    if project.ai_provider:
        db_project.ai_provider = project.ai_provider
    if project.ai_model is not None:
        db_project.ai_model = project.ai_model
    
    db.commit()
    return {"message": "Project updated successfully"}

@app.delete("/api/projects/{project_id}")
async def delete_project(project_id: int, db: Session = Depends(get_db)):
    """Delete project"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    db.delete(project)
    db.commit()
    return {"message": "Project deleted successfully"}

# ============= CHAPTER ENDPOINTS =============

@app.post("/api/projects/{project_id}/chapters")
async def create_chapter(project_id: int, chapter: ChapterCreate, db: Session = Depends(get_db)):
    """Create a new chapter"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    new_chapter = Chapter(
        project_id=project_id,
        chapter_number=chapter.chapter_number,
        title=chapter.title,
        original_text=chapter.original_text,
        status="pending"
    )
    db.add(new_chapter)
    db.commit()
    db.refresh(new_chapter)
    
    return {"id": new_chapter.id, "message": "Chapter created successfully"}

@app.get("/api/chapters/{chapter_id}")
async def get_chapter(chapter_id: int, db: Session = Depends(get_db)):
    """Get chapter details"""
    chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")
    
    return {
        "id": chapter.id,
        "project_id": chapter.project_id,
        "chapter_number": chapter.chapter_number,
        "title": chapter.title,
        "original_text": chapter.original_text,
        "translated_text": chapter.translated_text,
        "status": chapter.status,
        "translation_stats": chapter.translation_stats,
        "created_at": chapter.created_at.isoformat(),
        "updated_at": chapter.updated_at.isoformat()
    }

@app.put("/api/chapters/{chapter_id}")
async def update_chapter(chapter_id: int, chapter: ChapterUpdate, db: Session = Depends(get_db)):
    """Update chapter"""
    db_chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()
    if not db_chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")
    
    if chapter.title is not None:
        db_chapter.title = chapter.title
    if chapter.original_text is not None:
        db_chapter.original_text = chapter.original_text
    if chapter.translated_text is not None:
        db_chapter.translated_text = chapter.translated_text
    
    db.commit()
    return {"message": "Chapter updated successfully"}

@app.delete("/api/chapters/{chapter_id}")
async def delete_chapter(chapter_id: int, db: Session = Depends(get_db)):
    """Delete chapter"""
    chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")
    
    db.delete(chapter)
    db.commit()
    return {"message": "Chapter deleted successfully"}

# ============= TRANSLATION ENDPOINTS =============

@app.post("/api/translate")
async def translate_chapter(request: TranslationRequest, db: Session = Depends(get_db)):
    """Translate a chapter"""
    try:
        engine = TranslationEngine(db)
        result = await engine.translate_chapter(request.chapter_id, request.extract_terms)
        
        if not result["success"]:
            error_msg = result.get("error", "Translation failed")
            print(f"❌ Translation error: {error_msg}")
            raise HTTPException(status_code=500, detail=error_msg)
        
        print(f"✅ Chapter {result.get('chapter_id')} translated successfully")
        return result
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Unexpected error in translate_chapter: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/projects/{project_id}/statistics")
async def get_statistics(project_id: int, db: Session = Depends(get_db)):
    """Get translation statistics for a project"""
    engine = TranslationEngine(db)
    try:
        stats = engine.get_translation_statistics(project_id)
        return stats
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

# ============= GLOSSARY ENDPOINTS =============

@app.get("/api/projects/{project_id}/glossary")
async def get_glossary(project_id: int, db: Session = Depends(get_db)):
    """Get project glossary"""
    entries = db.query(GlossaryEntry).filter(
        GlossaryEntry.project_id == project_id
    ).order_by(GlossaryEntry.usage_count.desc()).all()
    
    return [
        {
            "id": e.id,
            "original_term": e.original_term,
            "translated_term": e.translated_term,
            "term_type": e.term_type,
            "context": e.context,
            "usage_count": e.usage_count,
            "confirmed": e.confirmed
        }
        for e in entries
    ]

@app.post("/api/projects/{project_id}/glossary")
async def add_glossary_entry(project_id: int, entry: GlossaryCreate, db: Session = Depends(get_db)):
    """Add glossary entry"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    new_entry = GlossaryEntry(
        project_id=project_id,
        original_term=entry.original_term,
        translated_term=entry.translated_term,
        term_type=entry.term_type,
        context=entry.context,
        confirmed=True
    )
    db.add(new_entry)
    db.commit()
    db.refresh(new_entry)
    
    return {"id": new_entry.id, "message": "Glossary entry added"}

@app.put("/api/glossary/{entry_id}")
async def update_glossary_entry(entry_id: int, entry: GlossaryCreate, db: Session = Depends(get_db)):
    """Update glossary entry"""
    db_entry = db.query(GlossaryEntry).filter(GlossaryEntry.id == entry_id).first()
    if not db_entry:
        raise HTTPException(status_code=404, detail="Glossary entry not found")
    
    db_entry.original_term = entry.original_term
    db_entry.translated_term = entry.translated_term
    db_entry.term_type = entry.term_type
    db_entry.context = entry.context
    db_entry.confirmed = True
    
    db.commit()
    return {"message": "Glossary entry updated"}

@app.delete("/api/glossary/{entry_id}")
async def delete_glossary_entry(entry_id: int, db: Session = Depends(get_db)):
    """Delete glossary entry"""
    entry = db.query(GlossaryEntry).filter(GlossaryEntry.id == entry_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Glossary entry not found")
    
    db.delete(entry)
    db.commit()
    return {"message": "Glossary entry deleted"}

# ============= ADVANCED GLOSSARY ENDPOINTS =============

@app.get("/api/glossary/{project_id}/search")
async def search_glossary(
    project_id: int,
    query: str = "",
    term_type: Optional[str] = None,
    confirmed_only: bool = False,
    db: Session = Depends(get_db)
):
    """Search glossary with filters"""
    glossary_service = GlossaryService(db)
    results = glossary_service.search_terms(project_id, query, term_type, confirmed_only)
    
    return [
        {
            "id": e.id,
            "original_term": e.original_term,
            "translated_term": e.translated_term,
            "term_type": e.term_type,
            "usage_count": e.usage_count,
            "confirmed": e.confirmed,
            "context": e.context
        }
        for e in results
    ]

@app.get("/api/glossary/{project_id}/stats")
async def get_glossary_stats(project_id: int, db: Session = Depends(get_db)):
    """Get glossary statistics"""
    glossary_service = GlossaryService(db)
    return glossary_service.get_statistics(project_id)

@app.get("/api/glossary/{project_id}/similar/{term}")
async def find_similar_glossary_terms(project_id: int, term: str, db: Session = Depends(get_db)):
    """Find similar terms for consistency checking"""
    glossary_service = GlossaryService(db)
    similar = glossary_service.find_similar_terms(project_id, term)
    return {"similar_terms": similar}

@app.post("/api/glossary/{project_id}/suggestions")
async def get_translation_suggestions(
    project_id: int,
    original_term: str,
    target_lang: str = "tr",
    db: Session = Depends(get_db)
):
    """Get translation suggestions for a term"""
    glossary_service = GlossaryService(db)
    suggestions = glossary_service.suggest_translations(original_term, target_lang)
    return {"suggestions": suggestions}

@app.post("/api/glossary/{project_id}/bulk-confirm")
async def bulk_confirm_terms(project_id: int, term_ids: List[int], db: Session = Depends(get_db)):
    """Confirm multiple terms at once"""
    glossary_service = GlossaryService(db)
    updated = glossary_service.bulk_confirm(project_id, term_ids)
    return {"message": f"{updated} terms confirmed"}

@app.post("/api/glossary/{project_id}/bulk-delete")
async def bulk_delete_terms(project_id: int, term_ids: List[int], db: Session = Depends(get_db)):
    """Delete multiple terms at once"""
    glossary_service = GlossaryService(db)
    deleted = glossary_service.bulk_delete(project_id, term_ids)
    return {"message": f"{deleted} terms deleted"}

@app.post("/api/glossary/{project_id}/bulk-update-type")
async def bulk_update_term_type(
    project_id: int,
    term_ids: List[int],
    new_type: str,
    db: Session = Depends(get_db)
):
    """Update type for multiple terms"""
    glossary_service = GlossaryService(db)
    updated = glossary_service.bulk_update_type(project_id, term_ids, new_type)
    return {"message": f"{updated} terms updated"}

@app.post("/api/glossary/{project_id}/merge-duplicates")
async def merge_duplicate_terms(project_id: int, db: Session = Depends(get_db)):
    """Merge duplicate glossary terms"""
    glossary_service = GlossaryService(db)
    merged = glossary_service.merge_duplicates(project_id)
    return {"message": f"{merged} duplicate terms merged"}

@app.get("/api/glossary/{project_id}/consistency")
async def check_consistency(project_id: int, db: Session = Depends(get_db)):
    """Check glossary consistency and find issues"""
    glossary_service = GlossaryService(db)
    analysis = glossary_service.analyze_consistency(project_id)
    return analysis

# ============= AI CONFIG ENDPOINTS =============

@app.get("/api/ai-providers")
async def list_providers():
    """List available AI providers"""
    providers = AIProviderFactory.get_available_providers()
    return {"providers": providers}

@app.get("/api/ai-configs")
async def list_ai_configs(db: Session = Depends(get_db)):
    """List all AI configurations"""
    configs = db.query(APIConfig).all()
    
    return [
        {
            "id": c.id,
            "provider_name": c.provider_name,
            "api_url": c.api_url,
            "model": c.model,
            "max_tokens": c.max_tokens,
            "temperature": c.temperature,
            "enabled": c.enabled,
            "has_api_key": bool(c.api_key)
        }
        for c in configs
    ]

@app.post("/api/ai-configs")
async def create_ai_config(config: APIConfigCreate, db: Session = Depends(get_db)):
    """Create or update AI configuration"""
    existing = db.query(APIConfig).filter(
        APIConfig.provider_name == config.provider_name
    ).first()
    
    if existing:
        # Only update api_key if a new one is provided
        if config.api_key:
            existing.api_key = config.api_key
        existing.api_url = config.api_url
        existing.model = config.model
        existing.max_tokens = config.max_tokens
        existing.temperature = config.temperature
        existing.enabled = config.enabled
        db.commit()
        return {"message": "AI configuration updated"}
    else:
        new_config = APIConfig(
            provider_name=config.provider_name,
            api_key=config.api_key,
            api_url=config.api_url,
            model=config.model,
            max_tokens=config.max_tokens,
            temperature=config.temperature,
            enabled=config.enabled
        )
        db.add(new_config)
        db.commit()
        return {"message": "AI configuration created"}

@app.delete("/api/ai-configs/{config_id}")
async def delete_ai_config(config_id: int, db: Session = Depends(get_db)):
    """Delete AI configuration"""
    config = db.query(APIConfig).filter(APIConfig.id == config_id).first()
    if not config:
        raise HTTPException(status_code=404, detail="Configuration not found")
    
    db.delete(config)
    db.commit()
    return {"message": "Configuration deleted"}

# ============= EXPORT ENDPOINTS =============

@app.get("/api/chapters/{chapter_id}/export")
async def export_chapter(chapter_id: int, format: str = "txt", db: Session = Depends(get_db)):
    """Export translated chapter"""
    chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")
    
    if not chapter.translated_text:
        raise HTTPException(status_code=400, detail="Chapter not yet translated")
    
    content = f"# Chapter {chapter.chapter_number}"
    if chapter.title:
        content += f": {chapter.title}"
    content += f"\n\n{chapter.translated_text}"
    
    return {
        "chapter_number": chapter.chapter_number,
        "title": chapter.title,
        "content": content,
        "format": format
    }

# ============= BATCH TRANSLATION ENDPOINTS =============

class BatchTranslateRequest(BaseModel):
    project_id: int
    chapter_ids: List[int]

@app.post("/api/batch/translate")
async def start_batch_translation(request: BatchTranslateRequest, db: Session = Depends(get_db)):
    """Start batch translation of multiple chapters"""
    try:
        batch_service = BatchTranslationService(db)
        job_id = await batch_service.create_batch_job(request.project_id, request.chapter_ids)
        
        # Start processing in background
        asyncio.create_task(batch_service.process_batch_job(job_id))
        
        return {"job_id": job_id, "message": "Batch translation started"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/batch/status/{job_id}")
async def get_batch_status(job_id: int, db: Session = Depends(get_db)):
    """Get status of a batch translation job"""
    batch_service = BatchTranslationService(db)
    status = batch_service.get_job_status(job_id)
    
    if not status:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return status

@app.post("/api/batch/cancel/{job_id}")
async def cancel_batch_translation(job_id: int, db: Session = Depends(get_db)):
    """Cancel a running batch job"""
    batch_service = BatchTranslationService(db)
    batch_service.cancel_job(job_id)
    return {"message": "Job cancelled"}

# ============= COST TRACKING ENDPOINTS =============

@app.get("/api/costs/project/{project_id}")
async def get_project_costs(project_id: int, db: Session = Depends(get_db)):
    """Get cost summary for a project"""
    costs = db.query(CostTracking).filter(CostTracking.project_id == project_id).all()
    
    total_cost = sum(c.estimated_cost for c in costs)
    total_tokens = sum(c.total_tokens for c in costs)
    
    return {
        "project_id": project_id,
        "total_cost": round(total_cost, 4),
        "total_tokens": total_tokens,
        "currency": "USD",
        "transactions": len(costs),
        "by_provider": _group_costs_by_provider(costs)
    }

@app.get("/api/costs/summary")
async def get_costs_summary(db: Session = Depends(get_db)):
    """Get overall cost summary"""
    all_costs = db.query(CostTracking).all()
    
    total_cost = sum(c.estimated_cost for c in all_costs)
    total_tokens = sum(c.total_tokens for c in all_costs)
    
    return {
        "total_cost": round(total_cost, 4),
        "total_tokens": total_tokens,
        "currency": "USD",
        "by_provider": _group_costs_by_provider(all_costs)
    }

def _group_costs_by_provider(costs):
    """Group costs by AI provider"""
    by_provider = {}
    for cost in costs:
        provider = cost.ai_provider
        if provider not in by_provider:
            by_provider[provider] = {
                "total_cost": 0,
                "total_tokens": 0,
                "count": 0
            }
        by_provider[provider]["total_cost"] += cost.estimated_cost
        by_provider[provider]["total_tokens"] += cost.total_tokens
        by_provider[provider]["count"] += 1
    
    return by_provider

# ============= EXPORT ENDPOINTS =============

@app.get("/api/export/project/{project_id}/{format}")
async def export_project(project_id: int, format: str, db: Session = Depends(get_db)):
    """Export entire project in various formats"""
    
    # Validate format
    if format not in ['pdf', 'epub', 'docx', 'txt']:
        raise HTTPException(status_code=400, detail="Invalid format. Use: pdf, epub, docx, or txt")
    
    # Get project and chapters
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    chapters = db.query(Chapter).filter(
        Chapter.project_id == project_id,
        Chapter.status == "completed"
    ).order_by(Chapter.chapter_number).all()
    
    if not chapters:
        raise HTTPException(status_code=400, detail="No completed chapters to export")
    
    # Prepare chapter data
    chapter_data = [
        {
            "chapter_number": c.chapter_number,
            "title": c.title,
            "translated_text": c.translated_text
        }
        for c in chapters
    ]
    
    # Prepare metadata
    metadata = {
        "description": project.description,
        "source_language": project.source_language,
        "target_language": project.target_language
    }
    
    # Export
    export_service = ExportService()
    
    try:
        if format == 'pdf':
            filepath = export_service.export_to_pdf(project.name, chapter_data, metadata)
        elif format == 'epub':
            filepath = export_service.export_to_epub(project.name, chapter_data, metadata)
        elif format == 'docx':
            filepath = export_service.export_to_docx(project.name, chapter_data, metadata)
        else:  # txt
            filepath = export_service.export_to_txt(project.name, chapter_data, metadata)
        
        return FileResponse(
            filepath,
            media_type='application/octet-stream',
            filename=os.path.basename(filepath)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")

# ============= BACKUP ENDPOINTS =============

@app.post("/api/backup/create/{project_id}")
async def create_backup(project_id: int, db: Session = Depends(get_db)):
    """Create a backup of a project"""
    try:
        backup_service = BackupService(db)
        filepath = backup_service.create_backup(project_id, backup_type="manual")
        
        return {
            "message": "Backup created successfully",
            "filepath": filepath
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/backup/list")
async def list_backups(project_id: Optional[int] = None, db: Session = Depends(get_db)):
    """List all backups"""
    backup_service = BackupService(db)
    backups = backup_service.list_backups(project_id)
    return backups

@app.post("/api/backup/restore")
async def restore_backup(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Restore a project from backup"""
    try:
        # Save uploaded file temporarily
        temp_path = f"temp_backup_{datetime.now().timestamp()}.zip"
        with open(temp_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Restore
        backup_service = BackupService(db)
        project_id = backup_service.restore_backup(temp_path)
        
        # Clean up
        os.remove(temp_path)
        
        return {
            "message": "Backup restored successfully",
            "project_id": project_id
        }
    except Exception as e:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/backup/{backup_id}")
async def delete_backup(backup_id: int, db: Session = Depends(get_db)):
    """Delete a backup"""
    try:
        backup_service = BackupService(db)
        backup_service.delete_backup(backup_id)
        return {"message": "Backup deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============= GLOSSARY IMPORT/EXPORT ENDPOINTS =============

@app.post("/api/glossary/{project_id}/import")
async def import_glossary(project_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Import glossary from CSV/Excel"""
    try:
        # Read file
        content = await file.read()
        
        # Determine file type and read
        if file.filename.endswith('.csv'):
            df = pd.read_csv(BytesIO(content))
        elif file.filename.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(BytesIO(content))
        else:
            raise HTTPException(status_code=400, detail="Invalid file format. Use CSV or Excel")
        
        # Validate columns
        required_cols = ['original_term', 'translated_term']
        if not all(col in df.columns for col in required_cols):
            raise HTTPException(status_code=400, detail=f"File must contain columns: {required_cols}")
        
        # Import entries
        imported = 0
        for _, row in df.iterrows():
            # Check if entry exists
            existing = db.query(GlossaryEntry).filter(
                GlossaryEntry.project_id == project_id,
                GlossaryEntry.original_term == row['original_term']
            ).first()
            
            if not existing:
                entry = GlossaryEntry(
                    project_id=project_id,
                    original_term=row['original_term'],
                    translated_term=row['translated_term'],
                    term_type=row.get('term_type', 'general'),
                    context=row.get('context'),
                    confirmed=True
                )
                db.add(entry)
                imported += 1
        
        db.commit()
        
        return {
            "message": f"Successfully imported {imported} glossary terms",
            "imported_count": imported
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/glossary/{project_id}/export")
async def export_glossary(project_id: int, format: str = "csv", db: Session = Depends(get_db)):
    """Export glossary to CSV/Excel"""
    
    # Get glossary
    entries = db.query(GlossaryEntry).filter(
        GlossaryEntry.project_id == project_id
    ).all()
    
    if not entries:
        raise HTTPException(status_code=400, detail="No glossary terms to export")
    
    # Prepare data
    data = [
        {
            "original_term": e.original_term,
            "translated_term": e.translated_term,
            "term_type": e.term_type,
            "context": e.context,
            "usage_count": e.usage_count,
            "confirmed": e.confirmed
        }
        for e in entries
    ]
    
    df = pd.DataFrame(data)
    
    # Export
    output = BytesIO()
    if format == "csv":
        df.to_csv(output, index=False, encoding='utf-8-sig')
        filename = f"glossary_{project_id}.csv"
        media_type = "text/csv"
    else:  # excel
        df.to_excel(output, index=False, engine='openpyxl')
        filename = f"glossary_{project_id}.xlsx"
        media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    
    output.seek(0)
    
    from fastapi.responses import StreamingResponse
    return StreamingResponse(
        output,
        media_type=media_type,
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

# ============= CHAPTER REVISION ENDPOINTS =============

@app.post("/api/chapters/{chapter_id}/revise")
async def save_chapter_revision(
    chapter_id: int,
    translated_text: str,
    revision_note: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Save a revision of a chapter"""
    
    chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")
    
    # Save current version as revision
    if chapter.translated_text:
        revision = ChapterRevision(
            chapter_id=chapter_id,
            translated_text=chapter.translated_text,
            revision_note=revision_note or "Auto-saved before edit"
        )
        db.add(revision)
    
    # Update chapter
    chapter.translated_text = translated_text
    db.commit()
    
    return {"message": "Revision saved successfully"}

@app.get("/api/chapters/{chapter_id}/revisions")
async def get_chapter_revisions(chapter_id: int, db: Session = Depends(get_db)):
    """Get revision history for a chapter"""
    
    revisions = db.query(ChapterRevision).filter(
        ChapterRevision.chapter_id == chapter_id
    ).order_by(ChapterRevision.created_at.desc()).all()
    
    return [
        {
            "id": r.id,
            "translated_text": r.translated_text,
            "revision_note": r.revision_note,
            "revised_by": r.revised_by,
            "created_at": r.created_at.isoformat()
        }
        for r in revisions
    ]

# ============= USER SETTINGS ENDPOINTS =============

@app.get("/api/settings/{key}")
async def get_setting(key: str, db: Session = Depends(get_db)):
    """Get a user setting"""
    setting = db.query(UserSettings).filter(UserSettings.setting_key == key).first()
    if not setting:
        return {"key": key, "value": None}
    
    return {"key": key, "value": setting.setting_value}

@app.post("/api/settings/{key}")
async def save_setting(key: str, value: dict, db: Session = Depends(get_db)):
    """Save a user setting"""
    setting = db.query(UserSettings).filter(UserSettings.setting_key == key).first()
    
    if setting:
        setting.setting_value = value
        setting.updated_at = datetime.utcnow()
    else:
        setting = UserSettings(setting_key=key, setting_value=value)
        db.add(setting)
    
    db.commit()
    return {"message": "Setting saved"}

# ============= STATISTICS ENDPOINTS =============

@app.get("/api/stats/dashboard")
async def get_dashboard_stats(db: Session = Depends(get_db)):
    """Get comprehensive dashboard statistics"""
    
    # Projects
    total_projects = db.query(Project).count()
    
    # Chapters
    all_chapters = db.query(Chapter).all()
    total_chapters = len(all_chapters)
    completed_chapters = sum(1 for c in all_chapters if c.status == "completed")
    
    # Glossary
    total_glossary_terms = db.query(GlossaryEntry).count()
    
    # Costs
    all_costs = db.query(CostTracking).all()
    total_cost = sum(c.estimated_cost for c in all_costs)
    total_tokens = sum(c.total_tokens for c in all_costs)
    
    # By provider
    costs_by_provider = _group_costs_by_provider(all_costs)
    
    return {
        "projects": {
            "total": total_projects
        },
        "chapters": {
            "total": total_chapters,
            "completed": completed_chapters,
            "pending": total_chapters - completed_chapters,
            "completion_rate": round((completed_chapters / total_chapters * 100) if total_chapters > 0 else 0, 2)
        },
        "glossary": {
            "total_terms": total_glossary_terms
        },
        "costs": {
            "total_cost": round(total_cost, 4),
            "total_tokens": total_tokens,
            "by_provider": costs_by_provider,
            "currency": "USD"
        }
    }

# Mount static files
if not os.path.exists("static"):
    os.makedirs("static")

app.mount("/static", StaticFiles(directory="static"), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)

