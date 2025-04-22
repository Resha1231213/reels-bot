# handlers/avatar_selection.py

from aiogram import Router, F
from aiogram.types import Message, InputMediaPhoto, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from states import FinalGenerateState
from pathlib import Path
import os

router = Router()

MAX_AVATARS = 5

@router.message(FinalGenerateState.waiting_for_avatar, F.photo)
async def handle_multiple_avatars(msg: Message, state: FSMContext):
    user_id = msg.from_user.id
    media_dir = Path(f"media/{user_id}/avatars")
    media_dir.mkdir(parents=True, exist_ok=True)

    existing = list(media_dir.glob("*.jpg"))
    if len(existing) >= MAX_AVATARS:
        await msg.answer("❌ Вы уже загрузили 5 аватаров. Выберите один для продолжения.")
        return

    photo = msg.photo[-1]
    file_path = media_dir / f"avatar_{len(existing)+1}.jpg"
    await photo.download(destination=file_path)

    await msg.answer(f"✅ Аватар {len(existing)+1} загружен. Отправьте ещё или выберите один из них для генерации.")

    existing.append(file_path)
    buttons = [[InlineKeyboardButton(text=f"Аватар {i+1}", callback_data=f"choose_avatar_{i}")]
               for i in range(len(existing))]
    markup = InlineKeyboardMarkup(inline_keyboard=buttons)
    await msg.answer("Выберите аватар:", reply_markup=markup)

@router.callback_query(F.data.startswith("choose_avatar_"))
async def choose_avatar(callback, state: FSMContext):
    idx = int(callback.data.split("_")[-1])
    user_id = callback.from_user.id
    avatar_path = Path(f"media/{user_id}/avatars/avatar_{idx+1}.jpg")

    await state.update_data(avatar=str(avatar_path))
    await callback.message.answer("✍️ Введите текст сценария:")
    await state.set_state(FinalGenerateState.enter_text)
    await callback.answer()
