from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from ..states import FeedbackStates

router = Router()

type_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="жалоба"), KeyboardButton(text="предложение")],
        [KeyboardButton(text="ошибка"), KeyboardButton(text="другое")]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

@router.message(Command("start"))
async def start_handler(message: Message, state: FSMContext):
    await message.answer(
        "Привет! Я бот для обратной связи по Вики-Пульс.\nВыбери тип обращения:",
        reply_markup=type_kb
    )
    await state.set_state(FeedbackStates.choosing_type)

@router.message(Command("cancel"))
async def cancel_handler(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is not None:
        await state.clear()
        await message.answer("Диалог отменён. Напиши /start чтобы начать заново.")
    else:
        await message.answer("Нет активного диалога. Напиши /start чтобы начать.")