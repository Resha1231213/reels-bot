# states/states.py

from aiogram.fsm.state import StatesGroup, State

class ReelsBotFlow(StatesGroup):
    # 1. Генерация аватара
    waiting_for_avatar_photo_or_video = State()
    confirm_avatar = State()

    # 2. Загрузка голоса
    waiting_for_voice_file_or_record = State()
    confirm_voice = State()

    # 3. Создание сценария
    enter_script_text_or_video_link = State()
    confirm_script = State()

    # 4. Парсинг рилса конкурента
    enter_competitor_link_or_choose_from_channel = State()
    confirm_parsed_video = State()

    # 5. Выбор языка
    select_voice_language = State()

    # 6. Выбор формата Reels
    select_video_format = State()  # full / 50/50 / circle

    # 7. Субтитры
    ask_add_subtitles = State()
    wait_for_custom_font = State()

    # 8. Оплата
    wait_for_payment_method = State()  # USDT / Юр. лицо
    confirm_payment = State()

    # 9. Подтверждение финальной сборки
    generating_final_video = State()
