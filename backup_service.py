"""
Backup Service - Automatic and manual project backups
"""
import os
import json
import zipfile
from datetime import datetime
from sqlalchemy.orm import Session
from database import Project, Chapter, GlossaryEntry, ProjectBackup


class BackupService:
    """Service for creating and managing project backups"""
    
    def __init__(self, db: Session):
        self.db = db
        self.backup_dir = "backups"
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)
    
    def create_backup(self, project_id: int, backup_type: str = "manual") -> str:
        """Create a backup of a project"""
        
        # Get project
        project = self.db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise ValueError("Project not found")
        
        # Create backup filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_name = "".join(c for c in project.name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        filename = f"{safe_name}_{timestamp}.zip"
        filepath = os.path.join(self.backup_dir, filename)
        
        # Create backup data
        backup_data = self._export_project_data(project_id)
        
        # Create ZIP file
        with zipfile.ZipFile(filepath, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add project data as JSON
            zipf.writestr('project_data.json', json.dumps(backup_data, ensure_ascii=False, indent=2))
            
            # Add README
            readme = self._generate_backup_readme(project, backup_data)
            zipf.writestr('README.txt', readme)
        
        # Get file size
        file_size = os.path.getsize(filepath)
        
        # Save backup record
        backup_record = ProjectBackup(
            project_id=project_id,
            backup_path=filepath,
            backup_size=file_size,
            backup_type=backup_type
        )
        self.db.add(backup_record)
        self.db.commit()
        
        return filepath
    
    def restore_backup(self, backup_path: str) -> int:
        """Restore a project from backup"""
        
        if not os.path.exists(backup_path):
            raise ValueError("Backup file not found")
        
        # Extract backup
        with zipfile.ZipFile(backup_path, 'r') as zipf:
            # Read project data
            project_data = json.loads(zipf.read('project_data.json').decode('utf-8'))
        
        # Create project
        project = Project(
            name=project_data['name'] + ' (Restored)',
            description=project_data.get('description'),
            source_language=project_data['source_language'],
            target_language=project_data['target_language'],
            ai_provider=project_data['ai_provider'],
            ai_model=project_data.get('ai_model')
        )
        self.db.add(project)
        self.db.commit()
        self.db.refresh(project)
        
        # Restore chapters
        for chapter_data in project_data.get('chapters', []):
            chapter = Chapter(
                project_id=project.id,
                chapter_number=chapter_data['chapter_number'],
                title=chapter_data.get('title'),
                original_text=chapter_data['original_text'],
                translated_text=chapter_data.get('translated_text'),
                status=chapter_data.get('status', 'pending')
            )
            self.db.add(chapter)
        
        # Restore glossary
        for entry_data in project_data.get('glossary', []):
            entry = GlossaryEntry(
                project_id=project.id,
                original_term=entry_data['original_term'],
                translated_term=entry_data['translated_term'],
                term_type=entry_data.get('term_type', 'general'),
                context=entry_data.get('context'),
                confirmed=entry_data.get('confirmed', True)
            )
            self.db.add(entry)
        
        self.db.commit()
        
        return project.id
    
    def _export_project_data(self, project_id: int) -> dict:
        """Export all project data"""
        
        # Get project
        project = self.db.query(Project).filter(Project.id == project_id).first()
        
        # Get chapters
        chapters = self.db.query(Chapter).filter(
            Chapter.project_id == project_id
        ).order_by(Chapter.chapter_number).all()
        
        # Get glossary
        glossary = self.db.query(GlossaryEntry).filter(
            GlossaryEntry.project_id == project_id
        ).all()
        
        # Build data structure
        data = {
            'project_name': project.name,
            'name': project.name,
            'description': project.description,
            'source_language': project.source_language,
            'target_language': project.target_language,
            'ai_provider': project.ai_provider,
            'ai_model': project.ai_model,
            'created_at': project.created_at.isoformat(),
            'backup_created_at': datetime.now().isoformat(),
            'version': '1.0',
            'chapters': [
                {
                    'chapter_number': c.chapter_number,
                    'title': c.title,
                    'original_text': c.original_text,
                    'translated_text': c.translated_text,
                    'status': c.status
                }
                for c in chapters
            ],
            'glossary': [
                {
                    'original_term': g.original_term,
                    'translated_term': g.translated_term,
                    'term_type': g.term_type,
                    'context': g.context,
                    'confirmed': g.confirmed,
                    'usage_count': g.usage_count
                }
                for g in glossary
            ],
            'statistics': {
                'total_chapters': len(chapters),
                'completed_chapters': sum(1 for c in chapters if c.status == 'completed'),
                'glossary_terms': len(glossary)
            }
        }
        
        return data
    
    def _generate_backup_readme(self, project, backup_data: dict) -> str:
        """Generate README for backup"""
        
        readme = f"""
{'=' * 60}
NOVEL TRANSLATOR - PROJECT BACKUP
{'=' * 60}

Project Name: {project.name}
Backup Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Version: 1.0

PROJECT INFORMATION:
-------------------
Source Language: {project.source_language}
Target Language: {project.target_language}
AI Provider: {project.ai_provider}

STATISTICS:
----------
Total Chapters: {backup_data['statistics']['total_chapters']}
Completed Chapters: {backup_data['statistics']['completed_chapters']}
Glossary Terms: {backup_data['statistics']['glossary_terms']}

CONTENTS:
--------
- project_data.json: Complete project data (can be imported back)

RESTORE INSTRUCTIONS:
--------------------
1. Open Novel Translator
2. Go to Settings > Backup
3. Click "Restore from Backup"
4. Select this backup file
5. Project will be restored with all data

{'=' * 60}
Generated by Novel Translator v1.0.0
{'=' * 60}
"""
        return readme.strip()
    
    def list_backups(self, project_id: int = None) -> list:
        """List all backups"""
        
        query = self.db.query(ProjectBackup)
        if project_id:
            query = query.filter(ProjectBackup.project_id == project_id)
        
        backups = query.order_by(ProjectBackup.created_at.desc()).all()
        
        return [
            {
                'id': b.id,
                'project_id': b.project_id,
                'backup_path': b.backup_path,
                'backup_size': b.backup_size,
                'backup_type': b.backup_type,
                'created_at': b.created_at.isoformat()
            }
            for b in backups
        ]
    
    def delete_backup(self, backup_id: int):
        """Delete a backup"""
        
        backup = self.db.query(ProjectBackup).filter(ProjectBackup.id == backup_id).first()
        if not backup:
            raise ValueError("Backup not found")
        
        # Delete file
        if os.path.exists(backup.backup_path):
            os.remove(backup.backup_path)
        
        # Delete record
        self.db.delete(backup)
        self.db.commit()

