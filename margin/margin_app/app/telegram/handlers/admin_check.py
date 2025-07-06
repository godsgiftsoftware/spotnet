from aiogram import Router, types
from aiogram.filters import Command
from app.telegram.filters.admin_filter import is_admin

router = Router()

@router.message(Command("admin_check"))
async def admin_check_handler(message: types.Message):
    if is_admin(message.from_user.id):
        await message.answer("✅ You are an admin!")
    else:
        await message.answer("❌ You aren’t an admin!")
