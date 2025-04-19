# voice.py
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.state import StatesGroup, State
from pathlib import Path

router = Router()

# FSM состояние для загрузки голоса
class VoiceState(StatesGroup):
    waiting_for_voice = State()

# Клавиатура "Продолжить"
def get_continue_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Продолжить", callback_data="continue_voice")]
    ])

# Путь к сохранению
def get_user_voice_path(user_id):
    path = Path(f"media/{user_id}/voice")
    path.mkdir(parents=True, exist_ok=True)
    return path

@router.message(F.text == "🎙 Загрузить голос")
async def ask_for_voice(message: Message, state: FSMContext):
    await state.set_state(VoiceState.waiting_for_voice)
    await message.answer("Пожалуйста, запишите голосовое сообщение или загрузите аудиофайл (mp3, wav).")

# Обработка голосового сообщения
@router.message(VoiceState.waiting_for_voice, F.voice)
async def save_voice(message: Message, state: FSMContext):
    user_id = message.from_user.id
    voice = message.voice
    path = get_user_voice_path(user_id)
    file_path = path / "voice.ogg"
    await voice.download(destination=file_path)
    await message.answer("Голосовое сообщение получено ✅", reply_markup=get_continue_keyboard())

# Обработка аудиофайла
@router.message(VoiceState.waiting_for_voice, F.audio)
async def save_audio(message: Message, state: FSMContext):
    user_id = message.from_user.id
    audio = message.audio
    path = get_user_voice_path(user_id)
    file_path = path / audio.file_name
    await audio.download(destination=file_path)
    await message.answer("Аудиофайл получен ✅", reply_markup=get_continue_keyboard())

@router.callback_query(F.data == "continue_voice")
async def proceed_to_script(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_reply_markup()
    await callback.message.answer("Теперь введите текст, сценарий или отправьте ссылку на ролик-конкурента.")
    # Здесь будет переход к следующему состоянию (ScriptState)
    # await state.set_state(ScriptState.waiting_for_input)
