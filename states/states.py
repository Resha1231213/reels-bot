@router.message(FinalGenerateState.upload_voice, F.voice | F.audio)
async def handle_voice(msg: Message, state: FSMContext):
    user_id = msg.from_user.id
    media_dir = Path(f"media/{user_id}")
    media_dir.mkdir(parents=True, exist_ok=True)

    voice_path = media_dir / "voice.ogg"

    if msg.voice:
        duration = msg.voice.duration
        if duration > 20:
            await msg.answer("❌ Голосовое сообщение слишком длинное. Пожалуйста, не более 20 секунд.")
            return
        await msg.voice.download(destination=voice_path)

    elif msg.audio:
        if msg.audio.duration and msg.audio.duration > 20:
            await msg.answer("❌ Аудиофайл слишком длинный. Пожалуйста, не более 20 секунд.")
            return
        await msg.audio.download(destination=voice_path)

    else:
        await msg.answer("❌ Отправьте именно голосовое сообщение или аудиофайл.")
        return

    await state.update_data(voice=str(voice_path))

    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🇷🇺 Русский"), KeyboardButton(text="🇬🇧 English")]
        ],
        resize_keyboard=True
    )

    await msg.answer("🌐 Выберите язык озвучки:", reply_markup=keyboard)
    await state.set_state(FinalGenerateState.select_language)
