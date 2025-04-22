# config.py

import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
HEYGEN_API_KEY = os.getenv("HEYGEN_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
