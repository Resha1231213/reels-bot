# handlers/parser.py

import re
import requests
from bs4 import BeautifulSoup
from openai import OpenAI

from config import OPENAI_API_KEY

openai = OpenAI(api_key=OPENAI_API_KEY)


def detect_platform(url: str) -> str:
    if "youtube.com" in url or "youtu.be" in url:
        return "youtube"
    elif "tiktok.com" in url:
        return "tiktok"
    elif "instagram.com" in url:
        return "instagram"
    return "unknown"


def parse_title_and_description(url: str) -> str:
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        # Универсальное извлечение title и description
        title = soup.title.string if soup.title else ""
        desc_tag = soup.find("meta", attrs={"name": "description"})
        description = desc_tag["content"] if desc_tag and "content" in desc_tag.attrs else ""

        return f"Title: {title}\nDescription: {description}"
    except Exception as e:
        return f"[Error parsing]: {e}"


def generate_script_from_url(url: str) -> str:
    platform = detect_platform(url)
    extracted = parse_title_and_description(url)

    prompt = (
        f"Ты — креативный сценарист для Instagram Reels. Клиент прислал ссылку на {platform}-видео."
        f"На основе информации ниже сгенерируй короткий сценарий (1 абзац) для ролика в этом стиле.\n\n"
        f"Информация о видео:\n{extracted}"
    )

    try:
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"[OpenAI Error]: {e}"
