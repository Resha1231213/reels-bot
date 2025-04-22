from aiogram.fsm.state import State, StatesGroup

class FinalGenerateState(StatesGroup):
    waiting_for_avatar = State()
    waiting_for_voice = State()
    enter_text_or_link = State()
    parsing_from_link = State()
    parsing_from_competitors = State()
    select_language = State()
    select_format = State()
    with_subtitles = State()
    font_upload = State()
    generating_video = State()

class AdminState(StatesGroup):
    waiting_for_activation = State()
