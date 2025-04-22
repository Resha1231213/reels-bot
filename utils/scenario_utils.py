import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

def extract_topic_from_url(url: str) -> str:
    # Пока упрощённо — вырезаем домен как тему (можно заменить на YouTube API или BeautifulSoup)
    if "youtube" in url:
        return "видео с YouTube на заданную тему"
    elif "tiktok" in url:
        return "видео из TikTok"
    elif "instagram" in url:
        return "видео из Instagram"
    else:
        return ""

def generate_script_with_openai(topic: str) -> str:
    prompt = f"Сгенерируй короткий, цепляющий сценарий для Reels на тему: {topic}. Добавь интригу, call-to-action и стиль инфлюенсера."
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return response["choices"][0]["message"]["content"].strip()
