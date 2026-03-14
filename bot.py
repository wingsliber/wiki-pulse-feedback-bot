from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
import asyncio
import datetime
from collections import defaultdict
import os
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

feedbacks = []  # Список для хранения фидбеков в памяти
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Словарь: {user_id: timestamp_последнего_фидбека} Нужно, чтобы не спамить записями (просто так)
last_feedback_time = defaultdict(lambda: datetime.datetime.min)
COOLDOWN_SECONDS = 60  # 1 минута между фидбеками

# Определяем шаги диалога
class FeedbackStates(StatesGroup):
    choosing_type = State()  # Выбор типа (кнопки)
    writing_text = State()   # Ввод текста
    confirming = State()     # Подтверждение (кнопка, которая завершает диалог)

# Кнопки для выбора типа
type_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="ошибка"), KeyboardButton(text="предложение")],
        [KeyboardButton(text="другое")]
    ],
    resize_keyboard=True,
    one_time_keyboard=True  # Кнопки исчезнут после выбора
)

confirm_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Да!"), KeyboardButton(text="Подумаю ещё")]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

@dp.message(Command("start"))
async def start_handler(message: Message, state: FSMContext):
    await message.answer(
        "Привет! Я бот для обратной связи по ИИ-помощнику Wiki-Пульс.\nЕсли захочешь прервать работу, напиши в любой момент /cancel\nС помощью кнопки выбери тип обращения:",
        reply_markup=type_kb
    )
    await state.set_state(FeedbackStates.choosing_type)

@dp.message(Command("cancel"))
async def cancel_handler(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is not None:
        await state.clear()
        await message.answer("Диалог отменён. Напиши /start чтобы начать заново.")
    else:
        await message.answer("Нет активного диалога. Напиши /start чтобы начать.")

@dp.message(FeedbackStates.choosing_type, F.text.in_({"ошибка", "предложение", "другое"}))
async def type_chosen(message: Message, state: FSMContext):
    await state.update_data(feedback_type=message.text)  # Сохраняем тип
    await message.answer(f"Тип выбран: {message.text}\nПожалуйста, напиши подробное описание, скриншоты прикладывай ссылкой.")
    await state.set_state(FeedbackStates.writing_text)

@dp.message(FeedbackStates.writing_text)
async def text_received(message: Message, state: FSMContext):
    feedback_text = message.text.strip()
    
    if not feedback_text:
        await message.answer("Текст не может быть пустым. Напиши своё обращение:")
        return
    
    if len(feedback_text) > 1000:
        await message.answer(
            f"Слишком длинно! Максимум 1000 символов, у тебя {len(feedback_text)}.\n"
            "Пожалуйста, сократи текст:"
        )
        return
    
    # Сохраняем текст ВО ВРЕМЕННОЕ СОСТОЯНИЕ (не в файл!)
    await state.update_data(feedback_text=feedback_text)
    
    # Показываем подтверждение
    await message.answer(
        f"Отправляю ваше обращение?\nТИП: { (await state.get_data())['feedback_type'] }\nТЕКСТ: {feedback_text[:50]}...",
        reply_markup=confirm_kb
    )
    await state.set_state(FeedbackStates.confirming)  # Переходим к подтверждению

@dp.message(FeedbackStates.confirming, F.text.in_({"Да!", "Подумаю ещё"}))
async def confirm_handler(message: Message, state: FSMContext):
    user_id = message.from_user.id
    now = datetime.datetime.now()
    
    if message.text == "Подумаю ещё":
        await state.clear()
        await message.answer("Хорошо, обращение не отправлено. Напиши /start чтобы начать заново.")
        return
    
    # === ПРОВЕРКА СПАМА (только при подтверждении!) ===
    if (now - last_feedback_time[user_id]).total_seconds() < COOLDOWN_SECONDS:
        remaining = int(COOLDOWN_SECONDS - (now - last_feedback_time[user_id]).total_seconds())
        await message.answer(f"⏳ Недавно ты уже писал обращение. Подожди ещё {remaining} секунд перед следующим обращением")
        await state.clear()  # Сбрасываем состояние
        return
    
    # === СОХРАНЕНИЕ (только при "Да!") ===
    last_feedback_time[user_id] = now
    data = await state.get_data()
    feedback_type = data["feedback_type"]
    feedback_text = data["feedback_text"]
    
    # Получаем читаемое имя
    user = message.from_user
    username = f"@{user.username}" if user.username else f"{user.first_name} (id:{user.id})"
    
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S")

    feedbacks.append({
        "timestamp": timestamp,
        "user": username,
        "type": feedback_type,
        "text": feedback_text
    })

    print(f"[СОХРАНЕНО] {timestamp} | {username} | {feedback_type} | {feedback_text[:50]}...")
    
    await message.answer("Спасибо! Твоё обращение сохранено и в скором времени будет обработано.")
    await state.clear()

async def main():
    print("Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())