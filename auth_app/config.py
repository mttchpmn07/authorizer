from functools import lru_cache
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    env_name: str = "Local"
    base_url: str = "http://localhost:8000"
    db_url: str = "sqlite:///./authorizer.db"
    secret_key: str = "b1358619ed784f3e2672e1bef403cc28dfba8b20ba7aceb1c5cd7417916939bd"
    algorythm: str = "HS256"
    access_token_expire_minutes: int = 30

    class Config:
        env_file = ".env"

@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    print(f"Loaded settings for: {settings.env_name}")
    return settings