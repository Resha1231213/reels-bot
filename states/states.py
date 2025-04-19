# states.py

from aiogram.fsm.state import StatesGroup, State

class GenerateState(StatesGroup):
    photo = State()
    voice = State()
    text = State()
    ready = State()

class FinalGenerateState(StatesGroup):
    waiting_for_avatar = State()
    enter_text = State()
    select_lang = State()
    select_format = State()
    with_subtitles = State()
