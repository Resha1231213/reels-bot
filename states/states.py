from aiogram.fsm.state import StatesGroup, State

class GenerateState(StatesGroup):
    photo = State()
    voice = State()
    text = State()
    ready = State()

class FinalGenerateState(StatesGroup):
    enter_text = State()             # Ввод текста сценария
    select_lang = State()            # Выбор языка
    select_format = State()          # Выбор формата видео
    select_subtitles = State()       # Выбор, нужны ли субтитры
    confirm_generation = State()     # Подтверждение генерации
    waiting_for_avatar = State()     # Загрузка аватара (фото)
    waiting_for_voice = State()      # Загрузка или запись голоса
    waiting_for_script = State()     # Ввод текста сценария
    waiting_for_confirmation = State()  # Подтверждение всех данных
