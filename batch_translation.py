"""
Batch Translation Service - Translate multiple chapters at once
"""
import asyncio
from typing import List, Dict
from sqlalchemy.orm import Session
from database import Chapter, TranslationJob
from translation_engine import TranslationEngine
from datetime import datetime


class BatchTranslationService:
    """Service for batch translating multiple chapters"""
    
    def __init__(self, db: Session):
        self.db = db
        self.engine = TranslationEngine(db)
        self.active_jobs = {}
    
    async def create_batch_job(self, project_id: int, chapter_ids: List[int]) -> int:
        """Create a new batch translation job"""
        
        # Validate chapters exist
        chapters = self.db.query(Chapter).filter(
            Chapter.id.in_(chapter_ids),
            Chapter.project_id == project_id
        ).all()
        
        if len(chapters) != len(chapter_ids):
            raise ValueError("Some chapters not found or don't belong to this project")
        
        # Create job
        job = TranslationJob(
            project_id=project_id,
            chapter_ids=chapter_ids,
            total_chapters=len(chapter_ids),
            status="pending"
        )
        
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        
        return job.id
    
    async def process_batch_job(self, job_id: int):
        """Process a batch translation job"""
        
        # Get job
        job = self.db.query(TranslationJob).filter(TranslationJob.id == job_id).first()
        if not job:
            raise ValueError("Job not found")
        
        # Update status
        job.status = "processing"
        job.started_at = datetime.utcnow()
        self.db.commit()
        
        # Store in active jobs
        self.active_jobs[job_id] = {
            'status': 'processing',
            'progress': 0,
            'current_chapter': None
        }
        
        completed = 0
        failed = []
        
        try:
            for chapter_id in job.chapter_ids:
                try:
                    # Update current status
                    self.active_jobs[job_id]['current_chapter'] = chapter_id
                    
                    # Translate chapter
                    result = await self.engine.translate_chapter(chapter_id, extract_terms=True)
                    
                    if result['success']:
                        completed += 1
                    else:
                        failed.append({
                            'chapter_id': chapter_id,
                            'error': result.get('error', 'Unknown error')
                        })
                    
                    # Update progress
                    progress = int((completed / job.total_chapters) * 100)
                    job.progress = progress
                    job.completed_chapters = completed
                    self.active_jobs[job_id]['progress'] = progress
                    self.db.commit()
                    
                except Exception as e:
                    failed.append({
                        'chapter_id': chapter_id,
                        'error': str(e)
                    })
            
            # Update final status
            job.completed_chapters = completed
            job.failed_chapters = failed
            job.status = "completed" if len(failed) == 0 else "failed"
            job.completed_at = datetime.utcnow()
            job.progress = 100
            
        except Exception as e:
            job.status = "failed"
            job.failed_chapters = failed + [{'error': str(e)}]
        
        finally:
            self.db.commit()
            if job_id in self.active_jobs:
                del self.active_jobs[job_id]
    
    def get_job_status(self, job_id: int) -> Dict:
        """Get status of a batch job"""
        
        # Check active jobs first
        if job_id in self.active_jobs:
            return self.active_jobs[job_id]
        
        # Get from database
        job = self.db.query(TranslationJob).filter(TranslationJob.id == job_id).first()
        if not job:
            return None
        
        return {
            'id': job.id,
            'status': job.status,
            'progress': job.progress,
            'total_chapters': job.total_chapters,
            'completed_chapters': job.completed_chapters,
            'failed_chapters': job.failed_chapters,
            'started_at': job.started_at.isoformat() if job.started_at else None,
            'completed_at': job.completed_at.isoformat() if job.completed_at else None
        }
    
    def cancel_job(self, job_id: int):
        """Cancel a running job"""
        if job_id in self.active_jobs:
            self.active_jobs[job_id]['status'] = 'cancelled'
        
        job = self.db.query(TranslationJob).filter(TranslationJob.id == job_id).first()
        if job and job.status == "processing":
            job.status = "cancelled"
            self.db.commit()

