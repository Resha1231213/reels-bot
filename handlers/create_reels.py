# handlers/create_reels.py

from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.types.input_file import FSInputFile
from states import FinalGenerateState
from handlers.generate import generate_reels
from pathlib import Path
import os
from utils.parser import extract_info_from_url

router = Router()

@router.message(F.text == "/create")
async def start_create(msg: Message, state: FSMContext):
    await msg.answer("📸 Пришлите до 5 фото или 1 видео для создания аватара")
    await state.set_state(FinalGenerateState.waiting_for_avatar)


@router.message(FinalGenerateState.waiting_for_avatar, F.photo | F.video)
async def handle_avatar(msg: Message, state: FSMContext):
    user_id = msg.from_user.id
    media_dir = Path(f"media/{user_id}")
    media_dir.mkdir(parents=True, exist_ok=True)

    if msg.photo:
        for i, photo in enumerate(msg.photo[-5:], start=1):
            file_path = media_dir / f"avatar_{i}.jpg"
            await photo.download(destination=file_path)
    elif msg.video:
        video = msg.video
        raw_path = media_dir / "avatar_video.mp4"
        await video.download(destination=raw_path)
        os.system(f"ffmpeg -i {raw_path} -ss 00:00:01.000 -vframes 1 {media_dir}/avatar_1.jpg")

    await msg.answer("🎙 Пришлите голосовое сообщение или аудиофайл для озвучки аватара")
    await state.set_state(FinalGenerateState.waiting_for_voice)


@router.message(FinalGenerateState.waiting_for_voice, F.voice | F.audio)
async def handle_voice(msg: Message, state: FSMContext):
    user_id = msg.from_user.id
    voice_path = Path(f"media/{user_id}/voice.ogg")

    voice_file = msg.voice or msg.audio
    await voice_file.download(destination=voice_path)

    await msg.answer("✍️ Введите текст или пришлите ссылку на видео, по которому нужно сделать сценарий")
    await state.set_state(FinalGenerateState.enter_text)


@router.message(FinalGenerateState.enter_text, F.text)
async def handle_text(msg: Message, state: FSMContext):
    await state.update_data(text=msg.text)
    keyboard = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="🇷🇺 Русский"), KeyboardButton(text="🇬🇧 English")]], resize_keyboard=True)
    await msg.answer("🌐 Выберите язык озвучки:", reply_markup=keyboard)
    await state.set_state(FinalGenerateState.select_language)


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
        text=data.get("text"),
        lang=data.get("language"),
        format_type=data.get("format"),
        with_subtitles=with_subs
    )

    if result:
        await msg.answer_video(FSInputFile(result), caption="🎬 Ваш Reels готов!")
    else:
        await msg.answer("❌ Ошибка генерации видео")

    await state.clear()


@router.message(F.text == "🔍 Найти рилс конкурента")
async def ask_competitor_link(msg: Message, state: FSMContext):
    await msg.answer("🔗 Пришли ссылку на рилс конкурента (TikTok, Instagram или YouTube)")
    await state.set_state(FinalGenerateState.waiting_for_competitor_link)


@router.message(FinalGenerateState.waiting_for_competitor_link, F.text)
async def parse_competitor_reel(msg: Message, state: FSMContext):
    url = msg.text.strip()
    title, description = extract_info_from_url(url)

    if not title and not description:
        await msg.answer("❌ Не удалось извлечь информацию. Попробуй другую ссылку.")
        return

    await msg.answer(f"✅ Найдено:\n<b>{title}</b>\n\n{description}")
    await state.update_data(comp_title=title, comp_desc=description)
    await state.set_state(FinalGenerateState.select_format)
