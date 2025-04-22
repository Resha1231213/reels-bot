from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InputMediaPhoto, InlineKeyboardMarkup, InlineKeyboardButton, Document
from aiogram.fsm.context import FSMContext
from states.FinalGenerateState import FinalGenerateState
from utils.video_editor import generate_reels
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
async def choose_avatar(callback: CallbackQuery, state: FSMContext):
    idx = int(callback.data.split("_")[-1])
    user_id = callback.from_user.id
    avatar_path = Path(f"media/{user_id}/avatars/avatar_{idx+1}.jpg")

    await state.update_data(avatar=str(avatar_path))
    await callback.message.answer("✍️ Введите текст сценария или отправьте ссылку на видео:")
    await state.set_state(FinalGenerateState.enter_script)
    await callback.answer()

@router.message(FinalGenerateState.enter_script)
async def handle_script_input(msg: Message, state: FSMContext):
    await state.update_data(script=msg.text)
    await msg.answer("Загрузите голос (аудиофайл или голосовое сообщение):")
    await state.set_state(FinalGenerateState.waiting_for_voice)

@router.message(FinalGenerateState.waiting_for_voice, F.voice | F.audio)
async def handle_voice(msg: Message, state: FSMContext):
    user_id = msg.from_user.id
    voice_dir = Path(f"media/{user_id}/voice")
    voice_dir.mkdir(parents=True, exist_ok=True)

    file = msg.voice or msg.audio
    voice_path = voice_dir / "voice.ogg"
    await file.download(destination=voice_path)
    await state.update_data(voice=str(voice_path))
    await msg.answer("Выберите формат видео:")
    await state.set_state(FinalGenerateState.select_format)

@router.message(FinalGenerateState.select_format)
async def choose_format(msg: Message, state: FSMContext):
    buttons = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🖼️ Fullscreen", callback_data="format_full")],
        [InlineKeyboardButton(text="🔀 50/50", callback_data="format_split")],
        [InlineKeyboardButton(text="⭕ Круглый аватар", callback_data="format_round")]
    ])
    await msg.answer("Выбери формат видео:", reply_markup=buttons)

@router.callback_query(F.data.startswith("format_"))
async def handle_format_choice(callback: CallbackQuery, state: FSMContext):
    await state.update_data(format=callback.data.replace("format_", ""))
    await callback.message.answer("Добавить субтитры?", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ С субтитрами", callback_data="subtitles_yes")],
        [InlineKeyboardButton(text="❌ Без субтитров", callback_data="subtitles_no")],
        [InlineKeyboardButton(text="⬆️ Загрузить свой шрифт", callback_data="subtitles_font")]
    ]))
    await state.set_state(FinalGenerateState.with_subtitles)
    await callback.answer()

@router.callback_query(FinalGenerateState.with_subtitles, F.data.startswith("subtitles_"))
async def handle_subtitles_choice(callback: CallbackQuery, state: FSMContext):
    choice = callback.data
replace("subtitles_", "")
    if choice == "yes":
        await state.update_data(subtitles=True)
        await callback.message.answer("Продолжим. Всё готово для генерации.")
        await state.set_state(FinalGenerateState.confirm_generate)
    elif choice == "no":
        await state.update_data(subtitles=False)
        await callback.message.answer("Продолжим. Всё готово для генерации.")
        await state.set_state(FinalGenerateState.confirm_generate)
    elif choice == "font":
        await callback.message.answer("Загрузи .ttf файл со шрифтом для субтитров:")
        await state.set_state(FinalGenerateState.upload_font)
    await callback.answer()

@router.message(FinalGenerateState.upload_font, F.document)
async def handle_font_upload(msg: Message, state: FSMContext):
    user_id = msg.from_user.id
    font_dir = Path(f"media/{user_id}/font")
    font_dir.mkdir(parents=True, exist_ok=True)
    path = font_dir / msg.document.file_name
    await msg.document.download(destination=path)
    await state.update_data(font=str(path))
    await msg.answer("✅ Шрифт загружен. Продолжим к генерации.")
    await state.set_state(FinalGenerateState.confirm_generate)

@router.message(FinalGenerateState.confirm_generate)
async def generate_final_reels(msg: Message, state: FSMContext):
    data = await state.get_data()
    result_path = generate_reels(
        avatar_path=data.get("avatar"),
        voice_path=data.get("voice"),
        script=data.get("script"),
        format=data.get("format"),
        subtitles=data.get("subtitles", False),
        font_path=data.get("font")
    )
    await msg.answer_video(video=open(result_path, "rb"), caption="🎬 Ваш Reels готов!")
    await state.clear()
