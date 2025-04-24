import asyncio
import logging
import os
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv

from handlers import create_reels, avatar_selection, start  # ДОБАВЬ start
from states import FinalGenerateState

# Загружаем переменные окружения из .env файла
load_dotenv()

# Получаем токен бота и ID админа из переменных окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
print(f"DEBUG BOT_TOKEN: {BOT_TOKEN}")
print(f"DEBUG ADMIN_ID: {ADMIN_ID}")

# Создаём экземпляры бота и диспетчера
bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=MemoryStorage())

# Регистрируем роутеры обработчиков
dp.include_router(start.router)              # <-- ЭТО ОБЯЗАТЕЛЬНО для кнопок!
dp.include_router(create_reels.router)
dp.include_router(avatar_selection.router)

# Основная асинхронная функция для запуска бота
async def main():
    logger.info("Bot is starting...")
    await dp.start_polling(bot)

# Запуск бота
if name == "__main__":
    asyncio.run(main())
