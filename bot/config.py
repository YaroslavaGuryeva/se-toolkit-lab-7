"""Configuration loader for the LMS bot.

Loads secrets from .env.bot.secret using pydantic-settings.
"""
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# Project root is parent of bot directory
BOT_DIR = Path(__file__).parent
PROJECT_ROOT = BOT_DIR.parent
ENV_FILE = PROJECT_ROOT / ".env.bot.secret"


class BotSettings(BaseSettings):
    """Bot configuration loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Telegram bot token
    bot_token: str = ""

    # LMS API configuration
    lms_api_base_url: str = "http://localhost:42002"
    lms_api_key: str = ""

    # LLM API configuration
    llm_api_model: str = "coder-model"
    llm_api_key: str = ""
    llm_api_base_url: str = "http://localhost:42005"


# Global settings instance
_settings: BotSettings | None = None


def get_settings() -> BotSettings:
    """Get the global settings instance, creating it if necessary."""
    global _settings
    if _settings is None:
        _settings = BotSettings()
    return _settings
