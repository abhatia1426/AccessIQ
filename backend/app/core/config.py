from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str

    # Auth
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Google
    GEMINI_API_KEY: str

    # App
    ENVIRONMENT: str = "development"
    CORS_ORIGINS: list[str] = ["http://localhost:5173"]

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    return Settings()