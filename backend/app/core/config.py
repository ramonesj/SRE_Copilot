"""
SRE Copilot Configuration
Enterprise-grade configuration management with environment variables
"""
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import field_validator
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Application
    APP_NAME: str = "SRE Copilot"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = "development"
    DEBUG: bool = True
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    API_TITLE: str = "SRE Copilot API"
    API_DESCRIPTION: str = "AI-Powered Site Reliability Engineering Platform"
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://sre_user:sre_password@localhost:5432/sre_copilot"
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10
    DATABASE_POOL_TIMEOUT: int = 30
    
    # JWT Authentication
    JWT_SECRET_KEY: str = "CHANGE-THIS-IN-PRODUCTION-USE-ENV-VARIABLE"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: List[str] = ["*"]
    CORS_ALLOW_HEADERS: List[str] = ["*"]
    
    # Storage Configuration
    STORAGE_PROVIDER: str = "local"  # "local" or "s3"
    STORAGE_PATH: str = "./storage"
    EVIDENCE_PATH: str = "./storage/evidence"
    AUDIT_PATH: str = "./storage/audit"
    
    # AWS Configuration (for production)
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: str = "us-east-1"
    S3_BUCKET_NAME: Optional[str] = None
    
    # AI/LLM Configuration
    LLM_PROVIDER: str = "openai"  # "openai", "bedrock", "azure"
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4"
    
    # AWS Bedrock Configuration
    BEDROCK_MODEL_ID: str = "anthropic.claude-3-sonnet-20240229-v1:0"
    
    # Azure OpenAI Configuration
    AZURE_OPENAI_API_KEY: Optional[str] = None
    AZURE_OPENAI_ENDPOINT: Optional[str] = None
    AZURE_OPENAI_DEPLOYMENT: Optional[str] = None
    
    # Observability
    PROMETHEUS_PORT: int = 9090
    GRAFANA_PORT: int = 3001
    ENABLE_METRICS: bool = True
    ENABLE_TRACING: bool = True
    
    # Risk Assessment Configuration
    RISK_SCORE_CRITICAL: int = 100
    RISK_SCORE_HIGH: int = 75
    RISK_SCORE_MEDIUM: int = 50
    RISK_SCORE_LOW: int = 25
    
    # Approval Configuration
    APPROVAL_TIMEOUT_SECONDS: int = 3600  # 1 hour
    AUTO_APPROVE_ENABLED: bool = False
    
    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Create global settings instance
settings = Settings()


# Ensure storage directories exist
def ensure_storage_directories():
    """Create storage directories if they don't exist"""
    os.makedirs(settings.STORAGE_PATH, exist_ok=True)
    os.makedirs(settings.EVIDENCE_PATH, exist_ok=True)
    os.makedirs(settings.AUDIT_PATH, exist_ok=True)


ensure_storage_directories()
