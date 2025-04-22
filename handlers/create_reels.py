# handlers/create_reels.py

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InputMediaPhoto, InlineKeyboardMarkup, InlineKeyboardButton, InputFile
from aiogram.fsm.context import FSMContext
from states.final_generate_state import FinalGenerateState
from handlers.generate import generate_reels
from pathlib import Path
import os

router = Router()

@router.message(FinalGenerateState.enter_text)
async def enter_text_handler(msg: Message, state: FSMContext):
    await state.update_data(script=msg.text)
    await msg.answer("Отправьте аудио (голос или файл), либо нажмите кнопку 'Пропустить'.")
    await state.set_state(FinalGenerateState.waiting_for_voice)

@router.message(FinalGenerateState.waiting_for_voice, F.voice | F.audio)
async def handle_voice(msg: Message, state: FSMContext):
    user_id = msg.from_user.id
    media_dir = Path(f"media/{user_id}/voice")
    media_dir.mkdir(parents=True, exist_ok=True)

    file = msg.voice or msg.audio
    path = media_dir / f"{file.file_id}.ogg"
    await file.download(destination=path)

    await state.update_data(voice=str(path))
    await msg.answer("Выберите язык озвучки:", reply_markup=InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="RU", callback_data="lang_ru")],
            [InlineKeyboardButton(text="EN", callback_data="lang_en")],
            [InlineKeyboardButton(text="FR", callback_data="lang_fr")],
        ]
    ))
    await state.set_state(FinalGenerateState.select_language)

@router.callback_query(FinalGenerateState.select_language, F.data.startswith("lang_"))
async def handle_language(callback: CallbackQuery, state: FSMContext):
    lang = callback.data.split("_")[1]
    await state.update_data(language=lang)
    await callback.message.answer("Выберите формат видео:", reply_markup=InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Фуллскрин", callback_data="format_full")],
            [InlineKeyboardButton(text="50/50", callback_data="format_split")],
            [InlineKeyboardButton(text="Аватар в круге", callback_data="format_circle")],
        ]
    ))
    await state.set_state(FinalGenerateState.select_format)
    await callback.answer()

@router.callback_query(FinalGenerateState.select_format, F.data.startswith("format_"))
async def handle_format(callback: CallbackQuery, state: FSMContext):
    format_value = callback.data.replace("format_", "")
    await state.update_data(format=format_value)
    await callback.message.answer("Добавить субтитры?", reply_markup=InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ С субтитрами", callback_data="subtitles_yes")],
            [InlineKeyboardButton(text="❌ Без субтитров", callback_data="subtitles_no")],
            [InlineKeyboardButton(text="Загрузить свой шрифт", callback_data="subtitles_font")]
        ]
    ))
    await state.set_state(FinalGenerateState.with_subtitles)
    await callback.answer()

@router.callback_query(FinalGenerateState.with_subtitles, F.data.startswith("subtitles_"))
async def handle_subtitles_choice(callback: CallbackQuery, state: FSMContext):
    choice = callback.data.replace("subtitles_", "")
    
    if choice == "yes":
        await state.update_data(subtitles=True)
        await callback.message.answer("✅ Субтитры выбраны. Всё готово для генерации.")
        await state.set_state(FinalGenerateState.confirm_generate)

    elif choice == "no":
        await state.update_data(subtitles=False)
        await callback.message.answer("👌 Без субтитров. Всё готово для генерации.")
        await state.set_state(FinalGenerateState.confirm_generate)

    elif choice == "font":
        await callback.message.answer("Загрузите .ttf файл со шрифтом для субтитров.")
        await state.set_state(FinalGenerateState.upload_font)

    await callback.answer()

@router.message(FinalGenerateState.upload_font, F.document)
async def handle_font_upload(msg: Message, state: FSMContext):
    user_id = msg.from_user.id
    font_dir = Path(f"media/{user_id}/font")
    font_dir.mkdir(parents=True, exist_ok=True)

    font_file = msg.document
    path = font_dir / font_file.file_name
    await font_file.download(destination=path)

    await state.update_data(font=str(path))
    await msg.answer("✅ Шрифт загружен. Продолжаем к генерации.")
    await state.set_state(FinalGenerateState.confirm_generate)

@router.message(FinalGenerateState.confirm_generate)
async def generate_final_reels(msg: Message, state: FSMContext):
    data = await state.get_data()

    avatar_path = data.get("avatar")
    voice_path = data.get("voice")
    script_data = data.get("script")
    format_data = data.get("format")
    subtitles = data.get("subtitles", False)
    font_path = data.get("font")
    lang = data.get("language", "ru")

    result_path = generate_reels(
        avatar_path=avatar_path,
        voice_path=voice_path,
        script=script_data,
        format=format_data,
        subtitles=subtitles,
        font_path=font_path,
        language=lang
    )

    await msg.answer_video(video=InputFile(result_path), caption="✅ Ваш Reels готов!")
    await state.clear()
