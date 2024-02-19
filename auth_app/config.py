from functools import lru_cache
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    env_name: str = "Local"
    base_url: str = "http://localhost:8000"
    db_url: str = "sqlite:///./authorizer.db"
    algorithm: str = "RS256"
    access_token_expire_minutes: int = 30

    class Config:
        env_file = ".env"

@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    print(f"Loaded settings for: {settings.env_name}")
    return settings