from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    
    # Database
    DATABASE_URL: str

    # Redis / Celery (This was missing!)
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"

    class Config:
        case_sensitive = True
        env_file = ".env"
        # This tells Pydantic: "If you find extra stuff in .env, just ignore it, don't crash"
        extra = "ignore"

settings = Settings()