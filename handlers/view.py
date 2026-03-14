from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from storage import get_feedbacks

router = Router()

# Список разрешённых пользователей (можно добавить)
ALLOWED_USERS = ["wingsliber"] 

@router.message(Command("view"))
async def view_handler(message: Message):
    # === ПРОВЕРКА: разрешён ли пользователь? ===
    user = message.from_user
    
    # Если у пользователя нет username (скрыт) или он не в списке разрешённых
    if not user.username or user.username not in ALLOWED_USERS:
        return
    
    # === ПОКАЗЫВАЕМ ФИДБЕКИ (только для разрешённых) ===
    feedback_list = get_feedbacks(limit=5)
    if not feedback_list:
        await message.answer("Пока нет обращений")
        return
    
    response = "Последние обращения:\n\n"
    for i, fb in enumerate(feedback_list, 1):
        response += f"{i}. [{fb['timestamp']}] {fb['user']}\n   {fb['type']}: {fb['text'][:100]}...\n\n"
    
    await message.answer(response)