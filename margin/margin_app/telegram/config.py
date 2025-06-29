
"""Configuration for the Telegram bot using pydantic-settings."""
from pydantic_settings import BaseSettings
from typing import List

class BotConfig(BaseSettings):
    """Bot configuration loaded from environment or .env.dev file."""
    bot_api_key: str
    admins: List[int]

    class Config:
        """Pydantic config for environment file location."""
        env_file = ".env.dev"
