from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # App Settings
    APP_NAME: str = "Novel Translator"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str = "sqlite:///./novel_translator.db"
    
    # API Keys (will be stored in database per user)
    DEFAULT_AI_PROVIDER: str = "gemini"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()

