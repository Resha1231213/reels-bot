# ✅ states/states.py — финальные состояния генерации Reels
from aiogram.fsm.state import State, StatesGroup

class FinalGenerateState(StatesGroup):
    waiting_for_avatar_files = State()   # Ожидаем фото или видео (до 5 штук)
    select_final_avatar = State()        # Пользователь выбирает, какой аватар использовать
    enter_text = State()                 # Ввод текста/сценария
    select_language = State()           # Выбор языка озвучки
    select_format = State()             # Выбор формата рилса
    with_subtitles = State()            # Нужно ли добавлять субтитры
