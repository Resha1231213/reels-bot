from aiogram.fsm.state import StatesGroup, State

class FinalGenerateState(StatesGroup):
    waiting_for_avatar = State()
    waiting_for_voice = State()
    enter_script = State()  # ← ВОТ ЭТОГО НЕ ХВАТАЕТ
    enter_link = State()
    competitor_ready = State()
    select_language = State()
    select_format = State()
    with_subtitles = State()
    upload_font = State()
    confirm_generate = State()
