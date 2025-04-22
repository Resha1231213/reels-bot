from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InputFile
from aiogram.fsm.context import FSMContext
from pathlib import Path
import os

from states import FinalGenerateState
from handlers.generate import generate_reels

router = Router()

@router.message(F.text == "/create")
async def start_create(msg: Message, state: FSMContext):
    await msg.answer("📸 Пришлите до 5 фото или 1 видео для создания аватара")
    await state.update_data(avatars=[])
    await state.set_state(FinalGenerateState.waiting_for_avatar)


@router.message(FinalGenerateState.waiting_for_avatar, F.photo | F.video)
async def handle_avatar(msg: Message, state: FSMContext):
    data = await state.get_data()
    user_id = msg.from_user.id
    media_dir = Path(f"media/{user_id}")
    media_dir.mkdir(parents=True, exist_ok=True)

    avatars = data.get("avatars", [])

    if msg.photo:
        file_path = media_dir / f"avatar_{len(avatars)+1}.jpg"
        await msg.photo[-1].download(destination=file_path)
        avatars.append(str(file_path))
    elif msg.video:
        raw_path = media_dir / "avatar_video.mp4"
        await msg.video.download(destination=raw_path)
        jpg_path = media_dir / "avatar.jpg"
        os.system(f"ffmpeg -i {raw_path} -ss 00:00:01.000 -vframes 1 {jpg_path}")
        avatars.append(str(jpg_path))

    await state.update_data(avatars=avatars)

    if len(avatars) >= 5 or msg.video:
        await msg.answer("🎙 Пришлите аудиофайл или запишите голос для озвучки")
        await state.set_state(FinalGenerateState.waiting_for_voice)
    else:
        await msg.answer(f"✅ Загружено: {len(avatars)}. Пришлите ещё или отправьте голос.")


@router.message(FinalGenerateState.waiting_for_voice)
async def handle_voice(msg: Message, state: FSMContext):
    user_id = msg.from_user.id
    media_dir = Path(f"media/{user_id}")

    if msg.voice:
        voice = await msg.voice.download(destination=media_dir / "voice.ogg")
    elif msg.audio:
        audio = await msg.audio.download(destination=media_dir / "voice.mp3")

    keyboard = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="✍️ Ввести текст"), KeyboardButton(text="🔗 Ссылка на видео")]], resize_keyboard=True)
    await msg.answer("📝 Выберите, как создать сценарий:", reply_markup=keyboard)
    await state.set_state(FinalGenerateState.enter_script)


@router.message(FinalGenerateState.enter_script, F.text)
async def handle_script_choice(msg: Message, state: FSMContext):
    if "текст" in msg.text.lower():
        await msg.answer("✍️ Введите текст для озвучки:", reply_markup=ReplyKeyboardRemove())
        await state.set_state(FinalGenerateState.enter_script)
    elif "ссылка" in msg.text.lower():
        await msg.answer("🔗 Пришлите ссылку на видео:", reply_markup=ReplyKeyboardRemove())
        await state.set_state(FinalGenerateState.enter_link)


@router.message(FinalGenerateState.enter_link)
async def handle_link(msg: Message, state: FSMContext):
    await state.update_data(link=msg.text)
    await msg.answer("🌐 Выберите язык озвучки:", reply_markup=ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="🇷🇺 Русский"), KeyboardButton(text="🇬🇧 English")]], resize_keyboard=True))
    await state.set_state(FinalGenerateState.select_language)


@router.message(FinalGenerateState.enter_script)
async def handle_text(msg: Message, state: FSMContext):
    await state.update_data(text=msg.text)
    await msg.answer("🌐 Выберите язык озвучки:", reply_markup=ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="🇷🇺 Русский"), KeyboardButton(text="🇬🇧 English")]], resize_keyboard=True))
    await state.set_state(FinalGenerateState.select_language)


@router.message(FinalGenerateState.select_language)
async def handle_language(msg: Message, state: FSMContext):
    lang = "ru" if "рус" in msg.text.lower() else "en"
    await state.update_data(language=lang)

    await msg.answer("🖼 Выберите формат видео:", reply_markup=ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="🟦 Fullscreen"), KeyboardButton(text="🔲 50/50")],
                 [KeyboardButton(text="⚪ Круглый аватар")]], resize_keyboard=True))
    await state.set_state(FinalGenerateState.select_format)


@router.message(FinalGenerateState.select_format)
async def handle_format(msg: Message, state: FSMContext):
    fmt = "full" if "full" in msg.text.lower() else "half" if "50" in msg.text else "circle"
    await state.update_data(format=fmt)

    await msg.answer("💬 Добавить субтитры?", reply_markup=ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="✅ С субтитрами"), KeyboardButton(text="❌ Без субтитров")]], resize_keyboard=True))
    await state.set_state(FinalGenerateState.with_subtitles)


@router.message(FinalGenerateState.with_subtitles)
async def handle_subtitles(msg: Message, state: FSMContext):
    with_subs = "✅" in msg.text
    await state.update_data(with_subtitles=with_subs)

    await msg.answer("🔤 Прикрепите .ttf шрифт для субтитров или нажмите 'Пропустить'", reply_markup=ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Пропустить")]], resize_keyboard=True))
    await state.set_state(FinalGenerateState.upload_font)


@router.message(FinalGenerateState.upload_font, F.document | F.text == "Пропустить")
async def handle_font(msg: Message, state: FSMContext):
    user_id = msg.from_user.id
    media_dir = Path(f"media/{user_id}")

    if msg.document:
        path = media_dir / msg.document.file_name
        await msg.document.download(destination=path)
        await state.update_data(font_path=str(path))
    else:
        await state.update_data(font_path=None)

    await msg.answer("🔄 Подтвердите генерацию рилса?", reply_markup=ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="🚀 Да"), KeyboardButton(text="❌ Отмена")]], resize_keyboard=True))
    await state.set_state(FinalGenerateState.confirm_generate)


@router.message(FinalGenerateState.confirm_generate, F.text == "🚀 Да")
async def handle_confirm(msg: Message, state: FSMContext):
    user_id = msg.from_user.id
    data = await state.get_data()

    result = generate_reels(
        user_id=user_id,
        avatars=data.get("avatars"),
        voice_path=f"media/{user_id}/voice.mp3",
        text=data.get("text"),
        link=data.get("link"),
        lang=data.get("language"),
        format_type=data.get("format"),
        with_subtitles=data.get("with_subtitles"),
        font_path=data.get("font_path")
    )

    if result:
        await msg.answer_document(InputFile(result), caption="🎬 Ваш Reels готов!")
    else:
        await msg.answer("❌ Ошибка генерации видео")

    await state.clear()


@router.message(FinalGenerateState.confirm_generate, F.text == "❌ Отмена")
async def handle_cancel(msg: Message, state: FSMContext):
    await msg.answer("❌ Генерация отменена", reply_markup=ReplyKeyboardRemove())
    await state.clear()
