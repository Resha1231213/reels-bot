from dotenv import load_dotenv
import os

# Загрузка переменных окружения из .env файла
load_dotenv()

# 🔐 Токен бота и Telegram ID админа
BOT_TOKEN = "8037568423:AAGyLt6a8EVq-CFbYcj1MbsE7tzeWi4jvyc"
ADMIN_ID = 621587126  # твой Telegram ID

# Для отладки — можно убрать потом
print("DEBUG BOT_TOKEN:", BOT_TOKEN)
print("DEBUG ADMIN_ID:", ADMIN_ID)
