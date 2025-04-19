from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

router = Router()

menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🧑 Сгенерировать аватар")],
        [KeyboardButton(text="🎙 Загрузить голос")],
        [KeyboardButton(text="📝 Ввести текст")],
        [KeyboardButton(text="🎬 Собрать Reels")],
        [KeyboardButton(text="📦 Мой пакет")],
    ],
    resize_keyboard=True,
)

@router.message(CommandStart())
async def start_handler(message: Message):
    await message.answer(
        f"Привет, {message.from_user.first_name}!\n\nДобро пожаловать в генератор Reels через ИИ 🎬",
        reply_markup=menu
    )
