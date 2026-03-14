from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from storage import get_feedbacks

router = Router()

@router.message(Command("view"))
async def view_handler(message: Message):
    feedback_list = get_feedbacks(limit=5)
    if not feedback_list:
        await message.answer("📭 Пока нет обращений")
        return
    
    response = "📋 Последние обращения:\n\n"
    for i, fb in enumerate(feedback_list, 1):
        response += f"{i}. [{fb['timestamp']}] {fb['user']}\n   {fb['type']}: {fb['text'][:50]}...\n\n"
    
    await message.answer(response)