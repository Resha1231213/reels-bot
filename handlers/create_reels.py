from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.types.input_file import FSInputFile
from states import ReelsBotFlow
from handlers.generate import generate_reels
from pathlib import Path
import os

router = Router()

@router.message(F.text == "/create")
async def cmd_create(msg: Message, state: FSMContext):
    await msg.answer("👤 Загрузите до 5 фото или одно видео для генерации аватара")
    await state.set_state(ReelsBotFlow.avatar)


@router.message(ReelsBotFlow.avatar, F.photo | F.video)
async def handle_avatar(msg: Message, state: FSMContext):
    user_id = msg.from_user.id
    media_dir = Path(f"media/{user_id}")
    media_dir.mkdir(parents=True, exist_ok=True)

    if msg.photo:
        photos = msg.photo[-1]
        file_path = media_dir / f"avatar_{len(list(media_dir.glob('avatar_*.jpg')))+1}.jpg"
        await photos.download(destination=file_path)
    elif msg.video:
        video = msg.video
        raw_path = media_dir / "avatar_video.mp4"
        await video.download(destination=raw_path)
        os.system(f"ffmpeg -i {raw_path} -ss 00:00:01.000 -vframes 1 {media_dir}/avatar_1.jpg")

    await msg.answer("🎙 Теперь запишите голос или загрузите файл для озвучки аватара")
    await state.set_state(ReelsBotFlow.voice)


@router.message(ReelsBotFlow.voice, F.voice | F.audio)
async def handle_voice(msg: Message, state: FSMContext):
    user_id = msg.from_user.id
    media_dir = Path(f"media/{user_id}")
    voice_path = media_dir / "voice.ogg"

    voice = msg.voice or msg.audio
    await voice.download(destination=voice_path)

    await msg.answer("📝 Введите сценарий или описание рилса")
    await state.set_state(ReelsBotFlow.script)


@router.message(ReelsBotFlow.script)
async def handle_script(msg: Message, state: FSMContext):
    await state.update_data(script=msg.text)
    await msg.answer("🔗 Пришлите ссылку на видео конкурента (или напишите 'пропустить')")
    await state.set_state(ReelsBotFlow.competitor)


@router.message(ReelsBotFlow.competitor)
async def handle_competitor(msg: Message, state: FSMContext):
    await state.update_data(competitor_url=msg.text)
    keyboard = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="🟦 Fullscreen"), KeyboardButton(text="🔲 50/50")],
        [KeyboardButton(text="⚪ Круглый аватар")]
    ], resize_keyboard=True)
    await msg.answer("🖼 Выберите формат Reels:", reply_markup=keyboard)
    await state.set_state(ReelsBotFlow.reels_format)


@router.message(ReelsBotFlow.reels_format)
async def handle_format(msg: Message, state: FSMContext):
    fmt = "full" if "Full" in msg.text else "half" if "50" in msg.text else "circle"
    await state.update_data(format=fmt)

    keyboard = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="✅ С субтитрами"), KeyboardButton(text="❌ Без субтитров")]
    ], resize_keyboard=True)
    await msg.answer("💬 Нужны ли субтитры?", reply_markup=keyboard)
    await state.set_state(ReelsBotFlow.subtitles)


@router.message(ReelsBotFlow.subtitles)
async def handle_subtitles(msg: Message, state: FSMContext):
    subs = "✅" in msg.text
    await state.update_data(with_subtitles=subs)

    await msg.answer("🌐 Выберите язык озвучки:",
                     reply_markup=ReplyKeyboardMarkup(
                         keyboard=[[KeyboardButton(text="🇷🇺 Русский"), KeyboardButton(text="🇬🇧 English")]],
                         resize_keyboard=True))
    await state.set_state(ReelsBotFlow.language)


@router.message(ReelsBotFlow.language)
async def handle_language(msg: Message, state: FSMContext):
    lang = "ru" if "Рус" in msg.text else "en"
    await state.update_data(language=lang)

    keyboard = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="✅ У меня есть активный пакет"), KeyboardButton(text="❌ Пока нет")]
    ], resize_keyboard=True)
    await msg.answer("📦 У вас активирован пакет на генерацию?", reply_markup=keyboard)
    await state.set_state(ReelsBotFlow.package_check)


@router.message(ReelsBotFlow.package_check)
async def handle_package_check(msg: Message, state: FSMContext):
    if "✅" in msg.text:
        data = await state.get_data()
        result = generate_reels(
            user_id=msg.from_user.id,
            text=data.get("script"),
            lang=data.get("language"),
            format_type=data.get("format"),
            with_subtitles=data.get("with_subtitles")
        )

        if result:
            await msg.answer_video(FSInputFile(result), caption="🎬 Ваш Reels готов!", reply_markup=ReplyKeyboardRemove())
        else:
            await msg.answer("❌ Ошибка генерации видео", reply_markup=ReplyKeyboardRemove())
    else:
        await msg.answer("💳 Оплатите пакет и повторите попытку позже", reply_markup=ReplyKeyboardRemove())

    await state.clear()
