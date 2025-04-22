from aiogram.fsm.state import StatesGroup, State

class ReelsBotFlow(StatesGroup):
    # Шаг 1: Загрузка аватара (фото или видео)
    waiting_for_avatar = State()
    
    # Шаг 2: Загрузка или запись голоса
    waiting_for_voice = State()

    # Шаг 3: Ввод текста или отправка ссылки/файла со сценарием
    waiting_for_script_input = State()

    # Шаг 4: Парсинг конкурентного Reels
    waiting_for_competitor_link = State()

    # Шаг 5: Выбор формата Reels (fullscreen, 50/50, круг)
    choosing_format = State()

    # Шаг 6: Субтитры — нужны/нет, свой шрифт
    choosing_subtitles = State()
    uploading_font = State()

    # Шаг 7: Подтверждение генерации Reels
    confirm_generation = State()

    # Шаг 8: Выбор пакета
    choosing_package = State()
    
    # Шаг 9: Проверка активации пакета
    package_check = State()

    # Финальный шаг — ожидание генерации
    generating_video = State()
