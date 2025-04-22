from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InputFile
from aiogram.fsm.context import FSMContext
from aiogram.types.input_file import FSInputFile
from states import FinalGenerateState
from handlers.generate import generate_reels
from pathlib import Path
import os

router = Router()

@router.message(F.text == "/create")
async def start_create(msg: Message, state: FSMContext):
    await msg.answer("📸 Пришлите до 5 фото или одно видео для создания аватара")
    await state.set_state(FinalGenerateState.waiting_for_avatar)


@router.message(FinalGenerateState.waiting_for_avatar, F.photo | F.video)
async def handle_avatar(msg: Message, state: FSMContext):
    user_id = msg.from_user.id
    media_dir = Path(f"media/{user_id}")
    media_dir.mkdir(parents=True, exist_ok=True)

    if msg.photo:
        photo = msg.photo[-1]
        file_path = media_dir / f"avatar_{len(list(media_dir.glob('avatar_*.jpg')))+1}.jpg"
        await photo.download(destination=file_path)

        if len(list(media_dir.glob('avatar_*.jpg'))) < 5:
            await msg.answer("📷 Фото добавлено. Пришлите ещё или нажмите 'Далее' если достаточно.",
                             reply_markup=ReplyKeyboardMarkup(
                                 keyboard=[[KeyboardButton(text="Далее")]], resize_keyboard=True))
            return
    elif msg.video:
        video = msg.video
        raw_path = media_dir / "avatar_video.mp4"
        await video.download(destination=raw_path)
        os.system(f"ffmpeg -i {raw_path} -ss 00:00:01.000 -vframes 1 {media_dir}/avatar_1.jpg")

    await msg.answer("🎤 Запишите голос аватара или загрузите аудиофайл")
    await state.set_state(FinalGenerateState.waiting_for_voice)


@router.message(FinalGenerateState.waiting_for_voice, F.voice | F.audio)
async def handle_voice(msg: Message, state: FSMContext):
    user_id = msg.from_user.id
    media_dir = Path(f"media/{user_id}")
    voice_path = media_dir / "voice.ogg"

    voice = msg.voice or msg.audio
    await voice.download(destination=voice_path)

    await msg.answer("✍️ Введите сценарий, который должен озвучить аватар")
    await state.set_state(FinalGenerateState.enter_script)


@router.message(FinalGenerateState.enter_script)
async def handle_script(msg: Message, state: FSMContext):
    await state.update_data(script=msg.text)
    await msg.answer("🔗 Если хотите, пришлите ссылку на видео (по теме которого будет рилс), или нажмите 'Пропустить'",
                     reply_markup=ReplyKeyboardMarkup(
                         keyboard=[[KeyboardButton(text="Пропустить")]], resize_keyboard=True))
    await state.set_state(FinalGenerateState.enter_link)


@router.message(FinalGenerateState.enter_link, F.text)
async def handle_link(msg: Message, state: FSMContext):
    if msg.text != "Пропустить":
        await state.update_data(link=msg.text)
    else:
        await state.update_data(link=None)

    await msg.answer("🌐 Выберите язык озвучки:",
                     reply_markup=ReplyKeyboardMarkup(
                         keyboard=[[KeyboardButton(text="🇷🇺 Русский"), KeyboardButton(text="🇬🇧 English")]], resize_keyboard=True))
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
    await state.update_data(with_subtitles=with_subs)

    await msg.answer("🔤 Загрузите файл шрифта (ttf/otf) или нажмите 'Пропустить'",
                     reply_markup=ReplyKeyboardMarkup(
                         keyboard=[[KeyboardButton(text="Пропустить")]], resize_keyboard=True))
    await state.set_state(FinalGenerateState.upload_font)


@router.message(FinalGenerateState.upload_font, F.document | F.text)
async def handle_font_or_skip(msg: Message, state: FSMContext):
    user_id = msg.from_user.id
    media_dir = Path(f"media/{user_id}")
    data = await state.get_data()

    if msg.document:
        font_path = media_dir / msg.document.file_name
        await msg.document.download(destination=font_path)
        data["font_path"] = str(font_path)
    else:
        data["font_path"] = None

    result = generate_reels(
        user_id=user_id,
        text=data.get("script"),
        lang=data.get("language"),
        format_type=data.get("format"),
        with_subtitles=data.get("with_subtitles"),
        font_path=data.get("font_path"),
        link=data.get("link")
    )

    if result:
        await msg.answer_video(FSInputFile(result), caption="🎬 Ваш Reels готов!")
    else:
        await msg.answer("❌ Ошибка генерации видео")

    await state.clear()
