from aiogram.fsm.state import State, StatesGroup

class FeedbackStates(StatesGroup):
    choosing_type = State()
    writing_text = State()
    confirming = State()