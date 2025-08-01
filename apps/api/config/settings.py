"""
Configuration Settings for Seraaj API
Centralized configuration management with environment-based settings
"""

import os
from typing import Dict, Any, List

try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseSettings
from pydantic import validator, Field
from enum import Enum


class Environment(str, Enum):
    """Application environments"""

    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"


class LogLevel(str, Enum):
    """Logging levels"""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class DatabaseConfig(BaseSettings):
    """Database configuration"""

    url: str = "sqlite:///./seraaj_dev.db"
    echo: bool = False
    pool_size: int = 5
    max_overflow: int = 10
    pool_pre_ping: bool = True
    pool_recycle: int = 300

    class Config:
        env_prefix = "DATABASE_"


class RedisConfig(BaseSettings):
    """Redis configuration for caching and sessions"""

    url: str = "redis://localhost:6379/0"
    max_connections: int = 10
    retry_on_timeout: bool = True
    socket_timeout: int = 5

    class Config:
        env_prefix = "REDIS_"


class SecurityConfig(BaseSettings):
    """Security configuration"""

    secret_key: str = "your-secret-key-here-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    password_min_length: int = 8
    max_login_attempts: int = 5
    lockout_duration_minutes: int = 15

    # CORS settings
    # Allow overriding via CORS_ORIGINS for simplicity
    cors_origins: str = os.getenv("CORS_ORIGINS", "")
    cors_allow_credentials: bool = True
    cors_allow_methods: List[str] = ["*"]
    cors_allow_headers: List[str] = ["*"]

    # Rate limiting
    rate_limit_enabled: bool = True
    default_rate_limit: int = 100  # requests per minute
    burst_rate_limit: int = 200

    class Config:
        env_prefix = "SECURITY_"

    @validator("secret_key")
    def validate_secret_key(cls, v):
        if len(v) < 32:
            raise ValueError("Secret key must be at least 32 characters long")
        return v

    def get_cors_origins_list(self) -> List[str]:
        """Parse comma-separated CORS origins string into list"""
        if not self.cors_origins:
            # Default development CORS origins
            return [
                "http://localhost:3030",
                "http://localhost:3000",
                "http://localhost:3031",
            ]
        return [
            origin.strip() for origin in self.cors_origins.split(",") if origin.strip()
        ]


class FileStorageConfig(BaseSettings):
    """File storage configuration"""

    backend: str = "local"  # "local" or "s3"
    upload_dir: str = "uploads"
    max_file_size_mb: int = 10
    allowed_image_types: List[str] = ["jpg", "jpeg", "png", "gif", "webp"]
    allowed_document_types: List[str] = ["pdf", "doc", "docx", "txt"]
    allowed_video_types: List[str] = ["mp4", "avi", "mov", "wmv"]

    # CDN settings
    cdn_enabled: bool = False
    cdn_base_url: str = ""

    # S3/Cloud storage settings
    cloud_storage_enabled: bool = False
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    aws_bucket_name: str = ""
    aws_region: str = "us-east-1"

    class Config:
        env_prefix = "FILE_STORAGE_"


class EmailConfig(BaseSettings):
    """Email configuration"""

    smtp_host: str = "localhost"
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_tls: bool = True
    smtp_ssl: bool = False

    from_email: str = "noreply@seraaj.org"
    from_name: str = "Seraaj"

    # Email templates
    templates_dir: str = "email_templates"

    # Third-party email services
    sendgrid_api_key: str = ""
    mailgun_api_key: str = ""
    mailgun_domain: str = ""

    class Config:
        env_prefix = "EMAIL_"


class MLConfig(BaseSettings):
    """Machine Learning configuration"""

    matching_algorithm: str = "collaborative_filtering"
    model_update_frequency_hours: int = 24
    min_training_data: int = 100
    similarity_threshold: float = 0.7

    # External ML services
    openai_api_key: str = ""
    huggingface_api_key: str = ""

    class Config:
        env_prefix = "ML_"


# Payment configuration removed - not part of MVP


class MonitoringConfig(BaseSettings):
    """Monitoring and observability configuration"""

    sentry_dsn: str = ""
    prometheus_enabled: bool = False
    prometheus_port: int = 8000

    # Logging
    log_level: LogLevel = LogLevel.INFO
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    log_file: str = "logs/seraaj.log"
    log_rotation: str = "midnight"
    log_retention_days: int = 30

    # Performance monitoring
    slow_query_threshold_ms: int = 1000
    slow_request_threshold_ms: int = 2000

    class Config:
        env_prefix = "MONITORING_"


class WebSocketConfig(BaseSettings):
    """WebSocket configuration"""

    max_connections: int = 1000
    heartbeat_interval: int = 30
    connection_timeout: int = 60
    message_queue_size: int = 100

    # Redis for WebSocket scaling
    redis_enabled: bool = False
    redis_channel_prefix: str = "seraaj:ws:"

    class Config:
        env_prefix = "WEBSOCKET_"


class APIConfig(BaseSettings):
    """API configuration"""

    title: str = "Seraaj API"
    description: str = "Two-sided volunteer marketplace for MENA nonprofits"
    version: str = "2.0.0"

    # API documentation
    docs_url: str = "/docs"
    redoc_url: str = "/redoc"
    openapi_url: str = "/openapi.json"

    # Request/Response settings
    max_request_size_mb: int = 50
    request_timeout_seconds: int = 30

    # Pagination defaults
    default_page_size: int = 20
    max_page_size: int = 100

    class Config:
        env_prefix = "API_"


class Settings(BaseSettings):
    """Main application settings"""

    # Environment
    environment: Environment = Field(Environment.DEVELOPMENT, alias="APP_ENV")
    debug: bool = False
    testing: bool = False
    auto_seed_on_startup: bool = Field(False, alias="AUTO_SEED_ON_STARTUP")

    # Host and port
    host: str = "0.0.0.0"
    port: int = 8000

    # Component configurations
    database: DatabaseConfig = DatabaseConfig()
    redis: RedisConfig = RedisConfig()
    security: SecurityConfig = SecurityConfig()
    file_storage: FileStorageConfig = FileStorageConfig()
    email: EmailConfig = EmailConfig()
    ml: MLConfig = MLConfig()
    monitoring: MonitoringConfig = MonitoringConfig()
    websocket: WebSocketConfig = WebSocketConfig()
    api: APIConfig = APIConfig()
    # payment: PaymentConfig removed - not part of MVP

    # Feature flags
    features: Dict[str, bool] = {
        "user_registration": True,
        "email_verification": True,
        "file_uploads": True,
        "real_time_messaging": True,
        "ml_matching": True,
        # Payment features removed - not part of MVP
        "skill_verification": True,
        # "payment_processing": False,  # removed - not part of MVP
        "advanced_analytics": True,
        "social_login": False,
        "pwa": True,
        "offline_support": True,
        "push_notifications": True,
        "background_sync": True,
        "web_share": True,
        "mobile_app_support": True,
        "notification_scheduling": True,
        "bulk_notifications": True,
        "notification_templates": True,
        "quiet_hours": True,
        "notification_analytics": True,
    }

    # Push notification settings
    vapid_private_key: str = "demo-vapid-private-key-placeholder"
    vapid_public_key: str = (
        "BEl62iUYgUivxIkv69yViEuiBIa40HI80NqIUHxHtjZHhr-RNZIwGKvlJ_SiuRzr3MZgJTBhOGXFu6_MmQhOhGE"
    )
    notification_retry_max: int = 3
    notification_cleanup_days: int = 30

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore",
    }

    @property
    def is_development(self) -> bool:
        return self.environment == Environment.DEVELOPMENT

    @property
    def is_production(self) -> bool:
        return self.environment == Environment.PRODUCTION

    @property
    def is_testing(self) -> bool:
        return self.environment == Environment.TESTING

    def get_database_url(self) -> str:
        """Get database URL based on environment"""
        if self.testing:
            return "sqlite:///:memory:"
        return self.database.url

    def get_cors_origins(self) -> List[str]:
        """Get CORS origins based on environment"""
        if self.is_production:
            # For production, still check environment variable first
            production_origins = self.security.get_cors_origins_list()
            if self.security.cors_origins:  # If environment variable is set
                return production_origins
            # Fallback to default production origins
            return [
                "https://seraaj.org",
                "https://www.seraaj.org",
                "https://app.seraaj.org",
            ]
        return self.security.get_cors_origins_list()

    def get_log_level(self) -> str:
        """Get log level based on environment"""
        if self.is_development:
            return LogLevel.DEBUG
        elif self.is_production:
            return LogLevel.WARNING
        return self.monitoring.log_level

    def feature_enabled(self, feature_name: str) -> bool:
        """Check if a feature is enabled"""
        return self.features.get(feature_name, False)

    @property
    def FILE_STORAGE(self) -> str:
        """Shortcut for storage backend type."""
        return self.file_storage.backend

    def get_upload_path(self, category: str = "") -> str:
        """Get upload path for files"""
        base_path = self.file_storage.upload_dir
        if category:
            return os.path.join(base_path, category)
        return base_path

    @validator("environment", pre=True)
    def validate_environment(cls, v):
        if isinstance(v, str):
            return Environment(v.lower())
        return v


# Global settings instance
settings = Settings()


# Configuration utilities
def get_database_config() -> Dict[str, Any]:
    """Get database configuration dictionary"""
    return {
        "url": settings.get_database_url(),
        "echo": settings.database.echo,
        "pool_size": settings.database.pool_size,
        "max_overflow": settings.database.max_overflow,
        "pool_pre_ping": settings.database.pool_pre_ping,
        "pool_recycle": settings.database.pool_recycle,
    }


def get_cors_config() -> Dict[str, Any]:
    """Get CORS configuration dictionary"""
    return {
        "allow_origins": settings.get_cors_origins(),
        "allow_credentials": settings.security.cors_allow_credentials,
        "allow_methods": settings.security.cors_allow_methods,
        "allow_headers": settings.security.cors_allow_headers,
    }


def get_logging_config() -> Dict[str, Any]:
    """Get logging configuration dictionary"""
    return {
        "level": settings.get_log_level(),
        "format": settings.monitoring.log_format,
        "filename": settings.monitoring.log_file if settings.is_production else None,
        "rotation": settings.monitoring.log_rotation,
        "retention": f"{settings.monitoring.log_retention_days} days",
    }


def validate_required_settings():
    """Validate that required settings are properly configured"""
    errors = []

    # Check required production settings
    if settings.is_production:
        if settings.security.secret_key == "your-secret-key-here-change-in-production":
            errors.append("SECRET_KEY must be changed in production")

        if not settings.database.url or "sqlite" in settings.database.url:
            errors.append("Production database must not be SQLite")

        if not settings.email.smtp_host:
            errors.append("Email configuration is required in production")

    # Check file storage settings
    if settings.file_storage.cloud_storage_enabled:
        if not all(
            [
                settings.file_storage.aws_access_key_id,
                settings.file_storage.aws_secret_access_key,
                settings.file_storage.aws_bucket_name,
            ]
        ):
            errors.append("AWS credentials required when cloud storage is enabled")

    if errors:
        raise ValueError(f"Configuration errors: {'; '.join(errors)}")


# Environment-specific configurations
def load_environment_config():
    """Load environment-specific configuration"""
    env_file = f".env.{settings.environment.value}"
    if os.path.exists(env_file):
        settings.Config.env_file = env_file
        settings.__init__()  # Reload settings
        print(f"Loaded environment config from {env_file}")


# Configuration presets
DEVELOPMENT_OVERRIDES = {
    "debug": True,
    "database": {"echo": True},
    "monitoring": {"log_level": LogLevel.DEBUG},
    "security": {"rate_limit_enabled": False},
}

PRODUCTION_OVERRIDES = {
    "debug": False,
    "database": {"echo": False},
    "monitoring": {"log_level": LogLevel.WARNING},
    "security": {"rate_limit_enabled": True},
}

TESTING_OVERRIDES = {
    "testing": True,
    "database": {"url": "sqlite:///:memory:"},
    "security": {"rate_limit_enabled": False},
    "email": {"smtp_host": "localhost"},
}


def apply_environment_overrides():
    """Apply environment-specific setting overrides"""
    if settings.is_development:
        overrides = DEVELOPMENT_OVERRIDES
    elif settings.is_production:
        overrides = PRODUCTION_OVERRIDES
    elif settings.is_testing:
        overrides = TESTING_OVERRIDES
    else:
        return

    # Apply overrides (this is a simplified version)
    for key, value in overrides.items():
        if hasattr(settings, key):
            if isinstance(value, dict):
                # Handle nested configurations
                config_obj = getattr(settings, key)
                for sub_key, sub_value in value.items():
                    if hasattr(config_obj, sub_key):
                        setattr(config_obj, sub_key, sub_value)
            else:
                setattr(settings, key, value)


# Initialize configuration
def initialize_config():
    """Initialize configuration system"""
    load_environment_config()
    apply_environment_overrides()
    validate_required_settings()

    print(f"Configuration initialized for {settings.environment.value} environment")
    print(f"Debug mode: {'enabled' if settings.debug else 'disabled'}")
    print(f"Database: {settings.get_database_url()}")
    print(f"Log level: {settings.get_log_level()}")


# Export commonly used configurations
__all__ = [
    "settings",
    "Environment",
    "LogLevel",
    "get_database_config",
    "get_cors_config",
    "get_logging_config",
    "initialize_config",
]
