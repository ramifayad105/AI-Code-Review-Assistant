from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    app_name: str = "AI-Code-Review-Assistant"
    debug: bool = False
    secret_key: str = "change-me-in-production"

    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/code_review"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # GitHub OAuth
    github_client_id: str = ""
    github_client_secret: str = ""
    github_webhook_secret: str = ""

    # OpenAI
    openai_api_key: str = ""
    openai_model: str = "gpt-4"

    # Ollama (alternative to OpenAI)
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "codellama"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    return Settings()
