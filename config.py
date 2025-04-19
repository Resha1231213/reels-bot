# config.py

from dotenv import load_dotenv
import os

# Загрузка переменных окружения из .env файла (локально)
load_dotenv()

# 🔐 Получаем токен бота и Telegram ID админа из переменных окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

# ✅ Для отладки — можешь убрать эти строки позже
print("DEBUG BOT_TOKEN:", BOT_TOKEN)
print("DEBUG ADMIN_ID:", ADMIN_ID)
