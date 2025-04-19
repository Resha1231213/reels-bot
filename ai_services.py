# ai_services.py

import os
import requests
import openai
from pathlib import Path

# Загружаем ключи из .env
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PLAYHT_API_KEY = os.getenv("PLAYHT_API_KEY")
PLAYHT_USER_ID = os.getenv("PLAYHT_USER_ID")

openai.api_key = OPENAI_API_KEY


# ✅ Генерация текста (GPT)
def generate_text_from_prompt(prompt: str) -> str:
    try:
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Ты пишешь короткий, эмоциональный сценарий для Reels."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"[OpenAI] Ошибка генерации текста: {e}")
        return ""


# ✅ Генерация озвучки (OpenAI)
def generate_speech(text: str, voice_id: str = "nova", user_id: int = 123456) -> str:
    print(f"[OpenAI] Озвучка текста: {text}")
    try:
        response = openai.audio.speech.create(
            model="tts-1",
            voice=voice_id,
            input=text
        )
        output_path = Path(f"media/{user_id}/voice_openai.mp3")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "wb") as f:
            f.write(response.content)
        return str(output_path)
    except Exception as e:
        print(f"[OpenAI] Ошибка озвучки: {e}")
        return ""


# ✅ Озвучка PlayHT (если нужно)
def generate_speech_playht(text: str, user_id: int = 123456, voice_id: str = "s3://voice-cloning-zero-shot/ru_default_voice_2.mp3") -> str:
    print(f"[PlayHT] Озвучка текста: {text}")
    try:
        headers = {
            "Authorization": f"Bearer {PLAYHT_API_KEY}",
            "X-User-Id": PLAYHT_USER_ID,
            "Content-Type": "application/json"
        }
        payload = {
            "text": text,
            "voice": voice_id,
            "output_format": "mp3"
        }
        response = requests.post("https://api.play.ht/api/v2/tts", json=payload, headers=headers)
        data = response.json()
        audio_url = data.get("audio_url")

        if not audio_url:
            raise Exception("[PlayHT] Не получен audio_url")

        audio_data = requests.get(audio_url).content
        output_path = Path(f"media/{user_id}/voice_playht.mp3")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "wb") as f:
            f.write(audio_data)

        return str(output_path)

    except Exception as e:
        print(f"[PlayHT] Ошибка озвучки: {e}")
        return ""
