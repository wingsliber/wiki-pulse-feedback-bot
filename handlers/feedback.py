from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from ..states import FeedbackStates
from ..storage import add_feedback, is_spam, update_last_time

router = Router()

# Кнопки подтверждения
confirm_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Да!"), KeyboardButton(text="Подумаю ещё")]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

@router.message(FeedbackStates.choosing_type, F.text.in_({"жалоба", "предложение", "ошибка", "другое"}))
async def type_chosen(message: Message, state: FSMContext):
    await state.update_data(feedback_type=message.text)
    await message.answer(f"Тип выбран: {message.text}\nНапиши текст обращения:")
    await state.set_state(FeedbackStates.writing_text)

@router.message(FeedbackStates.writing_text)
async def text_received(message: Message, state: FSMContext):
    feedback_text = message.text.strip()
    
    if not feedback_text:
        await message.answer("❌ Текст не может быть пустым. Напиши свой фидбек:")
        return
    
    if len(feedback_text) > 1000:
        await message.answer(
            f"❌ Слишком длинно! Максимум 1000 символов, у тебя {len(feedback_text)}.\n"
            "Пожалуйста, сократи текст:"
        )
        return
    
    await state.update_data(feedback_text=feedback_text)
    
    await message.answer(
        f"❓ Отправляю ваше обращение?\nТИП: {(await state.get_data())['feedback_type']}\nТЕКСТ: {feedback_text[:500]}...",
        reply_markup=confirm_kb
    )
    await state.set_state(FeedbackStates.confirming)

@router.message(FeedbackStates.confirming, F.text.in_({"Да!", "Подумаю ещё"}))
async def confirm_handler(message: Message, state: FSMContext):
    user_id = message.from_user.id
    
    if message.text == "Подумаю ещё":
        await state.clear()
        await message.answer("Хорошо, обращение не отправлено. Напиши /start чтобы начать заново.")
        return
    
    # === ПРОВЕРКА СПАМА ===
    spam, remaining = is_spam(user_id)
    if spam:
        await message.answer(f"⏳ Недавно ты уже писал обращение. Подожди ещё {remaining} секунд перед следующим обращением")
        await state.clear()
        return
    
    # === СОХРАНЕНИЕ ===
    update_last_time(user_id)
    
    data = await state.get_data()
    feedback_type = data["feedback_type"]
    feedback_text = data["feedback_text"]
    
    # Получаем читаемое имя
    user = message.from_user
    username = f"@{user.username}" if user.username else f"{user.first_name} (id:{user.id})"
    
    # Сохраняем в хранилище
    add_feedback(username, feedback_type, feedback_text)
    
    await message.answer("Спасибо! Твоё обращение сохранено и в скором времени будет обработано.")
    await state.clear()