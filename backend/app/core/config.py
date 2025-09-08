"""
Configuration settings for HTX Project
Uses Pydantic Settings for environment variable management
"""


from pydantic_settings import BaseSettings
from typing import List, Optional
import os
from dotenv import load_dotenv
from cryptography.fernet import Fernet
import logging

load_dotenv()

# Initialize logger
logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Application settings with Google Secret Manager integration"""
    
    # Environment
    ENV: str = "dev"
    
    # Secret Manager integration
    USE_SECRET_MANAGER: bool = False
    _secrets_manager = None
    
    # Application settings
    APP_NAME: str = "HTX Trading Analysis API"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Server settings
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8004
    
    # CORS settings
    ALLOWED_HOSTS: str = "http://localhost:3000,http://localhost:8080"
    
    @property
    def allowed_hosts_list(self) -> List[str]:
        """Parse ALLOWED_HOSTS from comma-separated string to list"""
        return [host.strip() for host in self.ALLOWED_HOSTS.split(",") if host.strip()]
    
    # Database settings
    DATABASE_URL: str = "sqlite+aiosqlite:///./data/app.db"
    DATABASE_ECHO: bool = False
    
    # HTX API settings
    # Для хранения зашифрованных ключей используйте переменные окружения
    HTX_API_KEY: Optional[str] = None
    HTX_API_SECRET: Optional[str] = None
    HTX_SUBUID: Optional[str] = None
    HTX_BASE_URL: str = "https://api.huobi.pro"

    # Ключ для шифрования (генерируйте и храните отдельно, не коммитьте в репозиторий)
    ENCRYPTION_KEY: Optional[str] = os.getenv("ENCRYPTION_KEY")

    def _get_secrets_manager(self):
        """Initialize and return secrets manager instance"""
        if self._secrets_manager is None and self.USE_SECRET_MANAGER and self.GCP_PROJECT_ID:
            try:
                from app.services.secret_manager import HTXSecretsManager
                self._secrets_manager = HTXSecretsManager(self.GCP_PROJECT_ID)
                logger.info("Google Secret Manager initialized")
            except ImportError:
                logger.warning("Secret Manager dependencies not available")
                self._secrets_manager = False  # Mark as unavailable
            except Exception as e:
                logger.error(f"Failed to initialize Secret Manager: {e}")
                self._secrets_manager = False
        return self._secrets_manager if self._secrets_manager is not False else None
    
    def get_secret(self, secret_name: str, env_fallback: Optional[str] = None) -> Optional[str]:
        """Get secret from Secret Manager or environment variable"""
        # Try Secret Manager first
        secrets_manager = self._get_secrets_manager()
        if secrets_manager:
            try:
                value = secrets_manager.secret_manager.get_secret(secret_name)
                if value:
                    return value
            except Exception as e:
                logger.debug(f"Failed to get secret {secret_name} from Secret Manager: {e}")
        
        # Fallback to environment variable
        env_key = env_fallback or secret_name.replace('-', '_').upper()
        env_value = os.getenv(env_key)
        
        # Try decryption if encrypted
        return self.decrypt(env_value)
    
    def decrypt(self, value: Optional[str]) -> Optional[str]:
        """Decrypt encrypted value using local encryption key"""
        if not value or not self.ENCRYPTION_KEY:
            return value
        try:
            f = Fernet(self.ENCRYPTION_KEY.encode())
            return f.decrypt(value.encode()).decode()
        except Exception:
            return value

    @property
    def htx_api_key(self) -> Optional[str]:
        """Get HTX API key from Secret Manager or environment"""
        return self.get_secret("htx-api-key", "HTX_API_KEY")

    @property
    def htx_api_secret(self) -> Optional[str]:
        """Get HTX API secret from Secret Manager or environment"""
        return self.get_secret("htx-api-secret", "HTX_API_SECRET")

    @property
    def htx_subuid(self) -> Optional[str]:
        """Get HTX sub-account UID from Secret Manager or environment"""
        return self.get_secret("htx-subuid", "HTX_SUBUID")
    
    @property
    def openai_api_key_secure(self) -> Optional[str]:
        """Get OpenAI API key from Secret Manager or environment"""
        return self.get_secret("openai-api-key", "OPENAI_API_KEY")
    
    @property
    def threecommas_api_key_secure(self) -> Optional[str]:
        """Get 3Commas API key from Secret Manager or environment"""
        return self.get_secret("threecommas-api-key", "THREECOMMAS_API_KEY")
    
    @property
    def threecommas_api_secret_secure(self) -> Optional[str]:
        """Get 3Commas API secret from Secret Manager or environment"""
        return self.get_secret("threecommas-api-secret", "THREECOMMAS_API_SECRET")
    
    # 3Commas API settings
    THREECOMMAS_API_KEY: Optional[str] = None
    THREECOMMAS_API_SECRET: Optional[str] = None
    THREECOMMAS_BASE_URL: str = "https://api.3commas.io/public/api"
    
    # Use secure property accessors for 3Commas
    @property
    def threecommas_api_key(self) -> Optional[str]:
        return self.threecommas_api_key_secure or self.THREECOMMAS_API_KEY
    
    @property
    def threecommas_api_secret(self) -> Optional[str]:
        return self.threecommas_api_secret_secure or self.THREECOMMAS_API_SECRET
    
    # File processing settings
    UPLOAD_DIR: str = "./data/raw"
    PROCESSED_DIR: str = "./data/processed"
    MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50MB
    ALLOWED_EXTENSIONS: str = ".csv,.xlsx,.xls"
    
    @property
    def allowed_extensions_list(self) -> List[str]:
        """Parse ALLOWED_EXTENSIONS from comma-separated string to list"""
        return [ext.strip() for ext in self.ALLOWED_EXTENSIONS.split(",") if ext.strip()]
    
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
    
    # OpenAI API settings
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL: str = "gpt-4o-mini"
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"
    OPENAI_MAX_TOKENS: int = 4000
    OPENAI_TEMPERATURE: float = 0.1
    
    # Use secure property accessor for OpenAI
    @property
    def openai_api_key(self) -> Optional[str]:
        return self.openai_api_key_secure or self.OPENAI_API_KEY
    
    # ML and Analytics settings
    ML_MODEL_CACHE_TTL: int = 3600  # 1 hour
    EMBEDDING_DIMENSIONS: int = 1536  # Default for text-embedding-3-small
    VECTOR_SIMILARITY_THRESHOLD: float = 0.8
    
    # Hardware configuration for local LLMs
    ML_DEVICE: str = "cpu"  # "cuda" or "cpu"
    LOAD_IN_4BIT: bool = True  # For memory efficiency
    TORCH_DTYPE: str = "float16"  # "float32" or "float16"
    
    # Google Cloud Platform (GCP) Configuration
    GCP_PROJECT_ID: Optional[str] = os.getenv("GCP_PROJECT_ID")
    GCP_REGION: str = "us-central1"
    GOOGLE_APPLICATION_CREDENTIALS: Optional[str] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    GCP_USE_DEFAULT_CREDENTIALS: bool = False  # Use default credentials when running in GCP
    
    # Cloud Storage Configuration
    GCP_STORAGE_BUCKET: str = "htx-trading-data"
    GCP_STORAGE_TEMP_BUCKET: str = "htx-trading-temp"
    GCP_STORAGE_UPLOAD_PREFIX: str = "uploads/"
    GCP_STORAGE_PROCESSED_PREFIX: str = "processed/"
    
    # Pub/Sub Topics Configuration
    PUBSUB_TRADE_INGESTED_TOPIC: str = "trade-ingested"
    PUBSUB_PARSING_COMPLETED_TOPIC: str = "parsing-completed"
    PUBSUB_MODEL_INFERENCE_TOPIC: str = "model-inference"
    PUBSUB_HTX_SYNC_TOPIC: str = "htx-sync-completed"
    
    # BigQuery Configuration
    BIGQUERY_DATASET: str = "trading_analytics"
    BIGQUERY_TRADES_TABLE: str = "trades"
    BIGQUERY_DEPOSITS_TABLE: str = "deposits"
    BIGQUERY_WITHDRAWALS_TABLE: str = "withdrawals"
    BIGQUERY_PREDICTIONS_TABLE: str = "ml_predictions"
    
    # Vertex AI Configuration
    VERTEX_AI_LOCATION: str = "us-central1"
    VERTEX_AI_STAGING_BUCKET: str = "htx-ml-staging"
    VERTEX_AI_MODEL_DISPLAY_NAME: str = "htx-trading-model"
    
    # Dataflow Configuration
    DATAFLOW_TEMP_LOCATION: str = "gs://htx-trading-temp/dataflow"
    DATAFLOW_STAGING_LOCATION: str = "gs://htx-trading-staging/dataflow"
    DATAFLOW_MACHINE_TYPE: str = "n1-standard-1"
    DATAFLOW_MAX_WORKERS: int = 10
    
    # Cloud Scheduler Configuration
    SCHEDULER_LOCATION: str = "us-central1"
    SCHEDULER_TIME_ZONE: str = "UTC"
    SCHEDULER_HTX_SYNC_SCHEDULE: str = "0 */1 * * *"  # Every hour
    SCHEDULER_DATAFLOW_SCHEDULE: str = "0 2 * * *"   # Daily at 2 AM
    SCHEDULER_MODEL_RETRAIN_SCHEDULE: str = "0 0 * * 0"  # Weekly on Sunday
    
    @property
    def gcp_enabled(self) -> bool:
        """Check if GCP integration is enabled"""
        return bool(self.GCP_PROJECT_ID and (
            self.GOOGLE_APPLICATION_CREDENTIALS or 
            self.GCP_USE_DEFAULT_CREDENTIALS
        ))
    
    @property
    def gcp_storage_enabled(self) -> bool:
        """Check if GCP Storage is configured"""
        return self.gcp_enabled and bool(self.GCP_STORAGE_BUCKET)
    
    @property
    def secret_manager_enabled(self) -> bool:
        """Check if Secret Manager integration is enabled and available"""
        return (
            self.USE_SECRET_MANAGER and 
            self.gcp_enabled and 
            self._get_secrets_manager() is not None
        )
    
    def enable_secret_manager(self) -> bool:
        """Enable Secret Manager integration if possible"""
        if not self.gcp_enabled:
            logger.warning("Cannot enable Secret Manager: GCP not configured")
            return False
        
        self.USE_SECRET_MANAGER = True
        success = self._get_secrets_manager() is not None
        
        if success:
            logger.info("Secret Manager integration enabled")
        else:
            logger.error("Failed to enable Secret Manager integration")
            self.USE_SECRET_MANAGER = False
        
        return success
    
    def validate_api_keys(self) -> dict:
        """Validate all API key configurations"""
        validation = {
            "htx": {
                "api_key": bool(self.htx_api_key),
                "api_secret": bool(self.htx_api_secret),
                "subuid": bool(self.htx_subuid),
                "configured": bool(self.htx_api_key and self.htx_api_secret)
            },
            "openai": {
                "api_key": bool(self.openai_api_key),
                "configured": bool(self.openai_api_key)
            },
            "threecommas": {
                "api_key": bool(self.threecommas_api_key),
                "api_secret": bool(self.threecommas_api_secret),
                "configured": bool(self.threecommas_api_key and self.threecommas_api_secret)
            },
            "gcp": {
                "project_id": bool(self.GCP_PROJECT_ID),
                "credentials": bool(self.GOOGLE_APPLICATION_CREDENTIALS),
                "secret_manager": self.secret_manager_enabled,
                "configured": self.gcp_enabled
            }
        }
        
        return validation
    
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
    
    # Validate GCP settings if enabled
    if settings.gcp_enabled:
        if not settings.GCP_PROJECT_ID:
            raise ValueError("GCP_PROJECT_ID is required when GCP is enabled")
        
        if not settings.GOOGLE_APPLICATION_CREDENTIALS and not settings.GCP_USE_DEFAULT_CREDENTIALS:
            raise ValueError(
                "Either GOOGLE_APPLICATION_CREDENTIALS or GCP_USE_DEFAULT_CREDENTIALS must be set"
            )


# Validate settings on import
validate_settings()

# Try to enable Secret Manager if GCP is configured
if settings.gcp_enabled and not settings.USE_SECRET_MANAGER:
    try:
        settings.enable_secret_manager()
    except Exception as e:
        logger.debug(f"Could not auto-enable Secret Manager: {e}")
