# handlers/create_reels.py

from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.types.input_file import FSInputFile
from states import FinalGenerateState
from handlers.generate import generate_reels
from pathlib import Path
import os

router = Router()

@router.message(F.text == "/create")
async def start_create(msg: Message, state: FSMContext):
    await msg.answer("📸 Пришлите фото или видео для создания аватара")
    await state.set_state(FinalGenerateState.waiting_for_avatar)


@router.message(FinalGenerateState.waiting_for_avatar, F.photo | F.video)
async def handle_avatar(msg: Message, state: FSMContext):
    user_id = msg.from_user.id
    media_dir = Path(f"media/{user_id}")
    media_dir.mkdir(parents=True, exist_ok=True)

    if msg.photo:
        photo = msg.photo[-1]
        file_path = media_dir / "avatar.jpg"
        await photo.download(destination=file_path)
    elif msg.video:
        video = msg.video
        raw_path = media_dir / "avatar_video.mp4"
        await video.download(destination=raw_path)
        os.system(f"ffmpeg -i {raw_path} -ss 00:00:01.000 -vframes 1 {media_dir}/avatar.jpg")

    await msg.answer("✍️ Введите текст или сценарий, который должен озвучить аватар")
    await state.set_state(FinalGenerateState.enter_text)


@router.message(FinalGenerateState.enter_text)
async def handle_text(msg: Message, state: FSMContext):
    await state.update_data(text=msg.text)
    keyboard = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="🇷🇺 Русский"), KeyboardButton(text="🇬🇧 English")]], resize_keyboard=True)
    await msg.answer("🌐 Выберите язык озвучки:", reply_markup=keyboard)
    await state.set_state(FinalGenerateState.select_lang)


@router.message(FinalGenerateState.select_language, F.text)
async def handle_language(msg: Message, state: FSMContext):
    lang = "ru" if "Рус" in msg.text else "en"
    await state.update_data(language=lang)

    keyboard = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="🟦 Fullscreen"), KeyboardButton(text="🔲 50/50")],
        [KeyboardButton(text="⚪ Круглый аватар")]
    ], resize_keyboard=True)
    await msg.answer("🖼 Выберите формат Reels:", reply_markup=keyboard)
    await state.set_state(FinalGenerateState.select_format)


@router.message(FinalGenerateState.select_format, F.text)
async def handle_format(msg: Message, state: FSMContext):
    fmt = "full" if "Full" in msg.text else "half" if "50" in msg.text else "circle"
    await state.update_data(format=fmt)

    keyboard = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="✅ С субтитрами"), KeyboardButton(text="❌ Без субтитров")]
    ], resize_keyboard=True)
    await msg.answer("💬 Нужны ли субтитры?", reply_markup=keyboard)
    await state.set_state(FinalGenerateState.with_subtitles)


@router.message(FinalGenerateState.with_subtitles, F.text)
async def handle_subtitles(msg: Message, state: FSMContext):
    with_subs = "✅" in msg.text
    data = await state.get_data()
    user_id = msg.from_user.id

    result = generate_reels(
        user_id=user_id,
        text=data["text"],
        lang=data["language"],
        format_type=data["format"],
        with_subtitles=with_subs
    )

    if result:
        await msg.answer_video(FSInputFile(result), caption="🎬 Ваш Reels готов!")
    else:
        await msg.answer("❌ Ошибка генерации видео")

    await state.clear()
