import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "ContractLens Legal AI"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # Secrets & Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "contractlens_super_secret_jwt_key_2026_dev_mode_change_in_prod")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440")) # 24 hours
    
    # Database (Supports PostgreSQL & SQLite Fallback)
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./contractlens.db")
    
    # LLM API
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")

    # Encrypted Object Storage (AWS S3 / MinIO / Local AES Fallback)
    STORAGE_ENCRYPTION_KEY: str = os.getenv("STORAGE_ENCRYPTION_KEY", "gAAAAABl-sample-fernet-key-32bytes-secret-devkey=")
    AWS_ACCESS_KEY_ID: Optional[str] = os.getenv("AWS_ACCESS_KEY_ID", None)
    AWS_SECRET_ACCESS_KEY: Optional[str] = os.getenv("AWS_SECRET_ACCESS_KEY", None)
    AWS_REGION_NAME: str = os.getenv("AWS_REGION_NAME", "ap-south-1")
    S3_BUCKET_NAME: str = os.getenv("S3_BUCKET_NAME", "contractlens-encrypted-docs")
    S3_ENDPOINT_URL: Optional[str] = os.getenv("S3_ENDPOINT_URL", None) # For MinIO / local S3 mock

    # Error Monitoring & Observability
    SENTRY_DSN: Optional[str] = os.getenv("SENTRY_DSN", None)
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: str = os.getenv("RATE_LIMIT_PER_MINUTE", "60/minute")

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()
