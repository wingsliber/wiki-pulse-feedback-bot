from aiogram import Dispatcher
from .start import router as start_router
from .feedback import router as feedback_router
from .view import router as view_router

def setup_handlers(dp: Dispatcher):
    """Регистрирует все хэндлеры в диспетчере"""
    dp.include_router(start_router)
    dp.include_router(feedback_router)
    dp.include_router(view_router)