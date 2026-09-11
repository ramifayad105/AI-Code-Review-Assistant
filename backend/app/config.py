from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    app_name: str = "AI-Code-Review-Assistant"
    debug: bool = False
    secret_key: str = "change-me-in-production"

    # Public base URL of this backend (used to build webhook callback URLs).
    # In production set this to your real domain, e.g. https://api.example.com
    base_url: str = "http://localhost:8000"

    # Comma-separated list of allowed CORS origins (the frontend URLs).
    cors_origins: str = "http://localhost:3000"

    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/code_review"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # GitHub OAuth
    github_client_id: str = ""
    github_client_secret: str = ""
    github_webhook_secret: str = ""

    # Symmetric key (Fernet) used to encrypt GitHub access tokens at rest.
    # Generate with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
    # If left empty, tokens are stored unencrypted (dev only — set this in production).
    token_encryption_key: str = ""

    # OpenAI
    openai_api_key: str = ""
    openai_model: str = "gpt-4"

    # Ollama (alternative to OpenAI)
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "codellama"

    # Max characters of a diff to send to the AI. Larger diffs are truncated
    # to protect against runaway cost and request timeouts.
    max_diff_chars: int = 40000

    @property
    def webhook_callback_url(self) -> str:
        """Full URL GitHub should POST webhook events to."""
        return f"{self.base_url.rstrip('/')}/webhooks/github"

    @property
    def cors_origins_list(self) -> list[str]:
        """CORS origins parsed into a list."""
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    return Settings()
