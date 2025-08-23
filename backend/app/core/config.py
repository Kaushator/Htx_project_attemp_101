"""
Configuration settings for HTX Project
Uses Pydantic Settings for environment variable management
"""

from pydantic_settings import BaseSettings
from typing import List, Optional
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # Environment
    ENV: str = "dev"
    
    # Application settings
    APP_NAME: str = "HTX Trading Analysis API"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Server settings
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    
    # CORS settings
    ALLOWED_HOSTS: List[str] = ["http://localhost:3000", "http://localhost:8080"]
    
    # Database settings
    DATABASE_URL: str = "sqlite+aiosqlite:///./data/app.db"
    DATABASE_ECHO: bool = False
    
    # HTX API settings
    HTX_API_KEY: Optional[str] = None
    HTX_API_SECRET: Optional[str] = None
    HTX_SUBUID: Optional[str] = None
    HTX_BASE_URL: str = "https://api.huobi.pro"
    
    # 3Commas API settings
    THREECOMMAS_API_KEY: Optional[str] = None
    THREECOMMAS_API_SECRET: Optional[str] = None
    THREECOMMAS_BASE_URL: str = "https://api.3commas.io/public/api"
    
    # File processing settings
    UPLOAD_DIR: str = "./data/raw"
    PROCESSED_DIR: str = "./data/processed"
    MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50MB
    ALLOWED_EXTENSIONS: List[str] = [".csv", ".xlsx", ".xls"]
    
    # Logging settings
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/htx_project.log"
    
    # Redis settings (for background tasks)
    REDIS_URL: str = "redis://localhost:6379"
    
    # Security settings
    JWT_SECRET: str = "change-me"
    JWT_EXPIRE_MINUTES: int = 43200
    
    # Analytics settings
    DEFAULT_CURRENCY: str = "USD"
    TIMEZONE: str = "UTC"
    
    # Background task settings
    ENABLE_BACKGROUND_TASKS: bool = True
    TASK_QUEUE_NAME: str = "htx_tasks"
    
    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 100
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create settings instance
settings = Settings()


# Validate required settings
def validate_settings():
    """Validate required settings"""
    if not settings.DATABASE_URL:
        raise ValueError("DATABASE_URL is required")
    
    # Create required directories
    directories = [
        settings.UPLOAD_DIR,
        settings.PROCESSED_DIR,
        os.path.dirname(settings.LOG_FILE)
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)


# Validate settings on import
validate_settings()
