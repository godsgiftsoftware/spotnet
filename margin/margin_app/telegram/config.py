
"""Configuration for the Telegram bot using pydantic-settings."""
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List

class BotConfig(BaseSettings):
    """Bot configuration loaded from environment variables."""
    BOT_API_KEY: str = Field(..., alias="BOT_API_KEY")
    ADMINS: List[int] = Field(..., alias="ADMINS")

    class Config:
        """Pydantic config for environment file location."""
        env_file = ".env.dev"
        case_sensitive = True
        extra = "ignore"    
