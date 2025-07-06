"""Handler for the /admin_check Telegram command to verify admin access."""

from aiogram import Router, types
from aiogram.filters import Command
from app.telegram.filters.admin_filter import is_admin

router = Router()

@router.message(Command("admin_check"))
async def admin_check_handler(message: types.Message):
    """
    Responds to the /admin_check command.

    Sends a confirmation if the user is an admin, otherwise denies access.
    """
    if is_admin(message.from_user.id):
        await message.answer("✅ You are an admin!")
    else:
        await message.answer("❌ You aren’t an admin!")
