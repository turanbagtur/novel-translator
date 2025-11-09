from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey, JSON, Boolean, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from config import settings

# Database setup
engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database Models
class Project(Base):
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    source_language = Column(String(10), default="en")
    target_language = Column(String(10), default="tr")
    ai_provider = Column(String(50), default="gemini")
    ai_model = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    chapters = relationship("Chapter", back_populates="project", cascade="all, delete-orphan")
    glossary_entries = relationship("GlossaryEntry", back_populates="project", cascade="all, delete-orphan")
    settings_data = Column(JSON, default={})


class Chapter(Base):
    __tablename__ = "chapters"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    chapter_number = Column(Integer, nullable=False)
    title = Column(String(500), nullable=True)
    original_text = Column(Text, nullable=False)
    translated_text = Column(Text, nullable=True)
    status = Column(String(20), default="pending")  # pending, processing, completed, error
    translation_stats = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    project = relationship("Project", back_populates="chapters")


class GlossaryEntry(Base):
    __tablename__ = "glossary_entries"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    original_term = Column(String(255), nullable=False, index=True)
    translated_term = Column(String(255), nullable=False)
    term_type = Column(String(50), default="general")  # character, location, skill, item, general
    context = Column(Text, nullable=True)
    usage_count = Column(Integer, default=0)
    confirmed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    project = relationship("Project", back_populates="glossary_entries")


class APIConfig(Base):
    __tablename__ = "api_configs"
    
    id = Column(Integer, primary_key=True, index=True)
    provider_name = Column(String(50), unique=True, nullable=False)
    api_key = Column(String(500), nullable=True)
    api_url = Column(String(500), nullable=True)
    model = Column(String(100), nullable=True)
    max_tokens = Column(Integer, default=4000)
    temperature = Column(Float, default=0.7)
    enabled = Column(Boolean, default=False)
    extra_config = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class TranslationCache(Base):
    __tablename__ = "translation_cache"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    source_text_hash = Column(String(64), index=True, nullable=False)
    source_text = Column(Text, nullable=False)
    translated_text = Column(Text, nullable=False)
    source_lang = Column(String(10))
    target_lang = Column(String(10))
    ai_provider = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)


class TranslationJob(Base):
    __tablename__ = "translation_jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    chapter_ids = Column(JSON, nullable=False)  # List of chapter IDs
    status = Column(String(20), default="pending")  # pending, processing, completed, failed
    progress = Column(Integer, default=0)  # 0-100
    total_chapters = Column(Integer, default=0)
    completed_chapters = Column(Integer, default=0)
    failed_chapters = Column(JSON, default=[])
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class CostTracking(Base):
    __tablename__ = "cost_tracking"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    chapter_id = Column(Integer, ForeignKey("chapters.id"), nullable=True)
    ai_provider = Column(String(50), nullable=False)
    input_tokens = Column(Integer, default=0)
    output_tokens = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    estimated_cost = Column(Float, default=0.0)
    currency = Column(String(3), default="USD")
    created_at = Column(DateTime, default=datetime.utcnow)


class ChapterRevision(Base):
    __tablename__ = "chapter_revisions"
    
    id = Column(Integer, primary_key=True, index=True)
    chapter_id = Column(Integer, ForeignKey("chapters.id"), nullable=False)
    translated_text = Column(Text, nullable=False)
    revision_note = Column(Text, nullable=True)
    revised_by = Column(String(100), default="user")
    created_at = Column(DateTime, default=datetime.utcnow)


class ProjectBackup(Base):
    __tablename__ = "project_backups"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    backup_path = Column(String(500), nullable=False)
    backup_size = Column(Integer, default=0)
    backup_type = Column(String(20), default="manual")  # manual, auto
    created_at = Column(DateTime, default=datetime.utcnow)


class UserSettings(Base):
    __tablename__ = "user_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    setting_key = Column(String(100), unique=True, nullable=False)
    setting_value = Column(JSON, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# Create all tables
def init_db():
    Base.metadata.create_all(bind=engine)


# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

