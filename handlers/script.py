from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pathlib import Path

from states.states import ScriptState, GenerateState  # ВАЖНО: добавлен импорт GenerateState

router = Router()

# Клавиатура выбора языка
def get_language_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru")],
        [InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en")],
        [InlineKeyboardButton(text="🇻🇳 Вьетнамский", callback_data="lang_vi")]
    ])

# Путь к сохранению текста
def get_user_script_path(user_id):
    path = Path(f"media/{user_id}/script")
    path.mkdir(parents=True, exist_ok=True)
    return path / "script.txt"

# Кнопка меню
@router.message(F.text == "📝 Ввести текст")
async def ask_for_script(message: Message, state: FSMContext):
    await state.set_state(ScriptState.waiting_for_input)
    await message.answer("Введите текст, сценарий или отправьте ссылку на видео-конкурента.")

# Сохраняем сценарий и спрашиваем язык
@router.message(ScriptState.waiting_for_input)
async def save_script_input(message: Message, state: FSMContext):
    user_id = message.from_user.id
    input_text = message.text
    path = get_user_script_path(user_id)

    with open(path, "w", encoding="utf-8") as f:
        f.write(input_text)

    await message.answer(
        "Текст/сценарий сохранён ✅\nТеперь выберите язык озвучки:",
        reply_markup=get_language_keyboard()
    )
    await state.set_state(GenerateState.choose_language)
