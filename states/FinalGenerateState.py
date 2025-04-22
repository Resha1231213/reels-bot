# states/FinalGenerateState.py

from aiogram.fsm.state import State, StatesGroup

class FinalGenerateState(StatesGroup):
    waiting_for_avatar = State()
    waiting_for_voice = State()
    enter_text = State()
    select_language = State()
    select_format = State()
    with_subtitles = State()
