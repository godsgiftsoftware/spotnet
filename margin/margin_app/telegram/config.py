from pydantic_settings import BaseSettings
from typing import List

class BotConfig(BaseSettings):
    bot_api_key: str
    admins: List[int]

    class Config:
        env_file = ".env.dev"
