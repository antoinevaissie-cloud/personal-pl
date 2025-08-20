from pydantic_settings import BaseSettings
from pydantic import Field, field_validator
from typing import List, Optional, Union
import os
from pathlib import Path

class Settings(BaseSettings):
    # Application
    app_name: str = "Personal P&L"
    debug: bool = Field(default=False, env="DEBUG")
    
    # Security
    secret_key: str = Field(default="change-me-in-production-please", env="SECRET_KEY")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7  # 7 days
    
    # CORS
    cors_origins: Union[List[str], str] = Field(
        default=["http://localhost:3000", "http://127.0.0.1:3000"],
        env="CORS_ORIGINS"
    )
    
    @field_validator('cors_origins', mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',')]
        return v
    
    # Database
    database_url: str = Field(default="data/finance.duckdb", env="DATABASE_URL")
    
    # API
    api_key: Optional[str] = Field(default=None, env="API_KEY")
    
    # File Upload
    max_upload_size: int = Field(default=10 * 1024 * 1024, env="MAX_UPLOAD_SIZE")  # 10MB
    allowed_extensions: List[str] = [".csv", ".CSV"]
    
    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_format: str = Field(default="json", env="LOG_FORMAT")  # json or console
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"  # Ignore extra fields from .env

settings = Settings()