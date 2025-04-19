from aiogram.fsm.state import StatesGroup, State

class GenerateState(StatesGroup):
    photo = State()
    voice = State()
    text = State()
    ready = State()

class FinalGenerateState(StatesGroup):
    enter_text = State()             # 🟡 ВОТ ЭТО ОБЯЗАТЕЛЬНО
    select_lang = State()
    select_format = State()
    select_subtitles = State()
    confirm_generation = State()
    waiting_for_avatar = State()
    waiting_for_voice = State()
    waiting_for_script = State()
    waiting_for_format = State()
    waiting_for_subtitles = State()
    waiting_for_confirmation = State()
