from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, FSInputFile
from aiogram.fsm.context import FSMContext
from states import ReelsBotFlow
from handlers.generate import generate_reels
from pathlib import Path
import os

router = Router()

@router.message(F.text == "/create")
async def start_create(msg: Message, state: FSMContext):
    await msg.answer("📸 Пришлите до 5 фото или 1 видео для создания аватара")
    await state.set_state(ReelsBotFlow.waiting_for_avatar)


@router.message(ReelsBotFlow.waiting_for_avatar, F.photo | F.video)
async def handle_avatar(msg: Message, state: FSMContext):
    user_id = msg.from_user.id
    media_dir = Path(f"media/{user_id}")
    media_dir.mkdir(parents=True, exist_ok=True)

    if msg.photo:
        for i, photo in enumerate(msg.photo[-5:], start=1):
            file_path = media_dir / f"avatar_{i}.jpg"
            await photo.download(destination=file_path)
        await state.update_data(avatar_path=str(file_path))

    elif msg.video:
        video = msg.video
        raw_path = media_dir / "avatar_video.mp4"
        await video.download(destination=raw_path)
        os.system(f"ffmpeg -i {raw_path} -ss 00:00:01.000 -vframes 1 {media_dir}/avatar_1.jpg")
        await state.update_data(avatar_path=str(media_dir / "avatar_1.jpg"))

    await msg.answer("🎙 Пришлите голос для аватара (аудиофайл или голосовое)")
    await state.set_state(ReelsBotFlow.waiting_for_voice)


@router.message(ReelsBotFlow.waiting_for_voice, F.voice | F.audio)
async def handle_voice(msg: Message, state: FSMContext):
    user_id = msg.from_user.id
    media_dir = Path(f"media/{user_id}")
    voice_path = media_dir / "voice.ogg"

    voice = msg.voice or msg.audio
    await voice.download(destination=voice_path)
    await state.update_data(voice_path=str(voice_path))

    await msg.answer("📝 Введите сценарий или пришлите ссылку на видео (Instagram, TikTok, YouTube)")
    await state.set_state(ReelsBotFlow.waiting_for_script)


@router.message(ReelsBotFlow.waiting_for_script, F.text)
async def handle_script(msg: Message, state: FSMContext):
    await state.update_data(script_input=msg.text)
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="🇷🇺 Русский"), KeyboardButton(text="🇬🇧 English")]],
        resize_keyboard=True
    )
    await msg.answer("🌐 Выберите язык озвучки:", reply_markup=keyboard)
    await state.set_state(ReelsBotFlow.waiting_for_language)


@router.message(ReelsBotFlow.waiting_for_language, F.text)
async def handle_language(msg: Message, state: FSMContext):
    lang = "ru" if "Рус" in msg.text else "en"
    await state.update_data(language=lang)

    keyboard = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="🟦 Fullscreen"), KeyboardButton(text="🔲 50/50")],
        [KeyboardButton(text="⚪ Круглый аватар")]
    ], resize_keyboard=True)
    await msg.answer("🖼 Выберите формат Reels:", reply_markup=keyboard)
    await state.set_state(ReelsBotFlow.waiting_for_format)


@router.message(ReelsBotFlow.waiting_for_format, F.text)
async def handle_format(msg: Message, state: FSMContext):
    fmt = "full" if "Full" in msg.text else "half" if "50" in msg.text else "circle"
    await state.update_data(format_type=fmt)

    keyboard = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="✅ С субтитрами"), KeyboardButton(text="❌ Без субтитров")]
    ], resize_keyboard=True)
    await msg.answer("💬 Добавить субтитры?", reply_markup=keyboard)
    await state.set_state(ReelsBotFlow.waiting_for_subtitles)


@router.message(ReelsBotFlow.waiting_for_subtitles, F.text)
async def handle_subtitles(msg: Message, state: FSMContext):
    with_subs = "✅" in msg.text
    data = await state.get_data()
    user_id = msg.from_user.id

    result = generate_reels(
        user_id=user_id,
        avatar_path=data["avatar_path"],
        voice_path=data["voice_path"],
        script_input=data["script_input"],
        lang=data["language"],
        format_type=data["format_type"],
        with_subtitles=with_subs
    )

    if result:
        await msg.answer_video(FSInputFile(result), caption="🎬 Ваш Reels готов!")
    else:
        await msg.answer("❌ Ошибка генерации Reels")

    await state.clear()
