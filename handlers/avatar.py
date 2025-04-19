from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import StateFilter
from aiogram.fsm.state import StatesGroup, State
import os
from pathlib import Path

router = Router()

# FSM состояния
class AvatarState(StatesGroup):
    waiting_for_avatar = State()

# Клавиатура "Продолжить"
def get_continue_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Продолжить", callback_data="continue_avatar")]
    ])

# Путь для сохранения фото
def get_user_avatar_path(user_id):
    path = Path(f"media/{user_id}/avatar")
    path.mkdir(parents=True, exist_ok=True)
    return path

# Обработка команды /start или нажатия на кнопку "Сгенерировать аватар"
@router.message(F.text == "🧑 Сгенерировать аватар")
async def ask_for_avatar(message: Message, state: FSMContext):
    await state.set_state(AvatarState.waiting_for_avatar)
    await message.answer("Отправьте фото или селфи, по которому нужно создать аватар. Можно до 5 штук.")

# Обработка полученного фото
@router.message(AvatarState.waiting_for_avatar, F.photo)
async def save_avatar_photo(message: Message, state: FSMContext):
    user_id = message.from_user.id
    photo = message.photo[-1]
    path = get_user_avatar_path(user_id)

    # Считаем уже сохранённые фото
    existing_photos = list(path.glob("*.jpg"))
    if len(existing_photos) >= 5:
        await message.answer("Вы уже загрузили 5 фото. Нажмите 'Продолжить'.")
