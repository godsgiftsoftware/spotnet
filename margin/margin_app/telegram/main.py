
"""Main entry point for the Telegram bot service."""
import asyncio
from aiogram import Bot, Dispatcher
from .config import BotConfig
from .handlers import start_router

async def main():
    """Initialize and run the Telegram bot."""
    config = BotConfig()
    bot = Bot(token=config.bot_api_key)
    dp = Dispatcher()
    dp.include_router(start_router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
