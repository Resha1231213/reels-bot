# main.py

import asyncio
import logging
import os
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv
from handlers import create_reels

# Загружаем переменные окружения
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

# Настройка логгера
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
print(f"DEBUG BOT_TOKEN: {BOT_TOKEN}")
print(f"DEBUG ADMIN_ID: {ADMIN_ID}")

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN, default=ParseMode.HTML)
dp = Dispatcher(storage=MemoryStorage())
dp.include_router(create_reels.router)


async def main():
    logger.info("Bot is starting...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
