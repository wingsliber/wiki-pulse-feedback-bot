from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from handlers import setup_handlers
import asyncio

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Регистрируем все хэндлеры
setup_handlers(dp)

async def main():
    print("Бот запущен!", flush=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())