import requests
import time
from pathlib import Path
import os

HEYGEN_API_KEY = os.getenv("HEYGEN_API_KEY=Y2EzNTJkMzUwZjZkNDM2NDliMDIwOTNjYjlmMmI3Y2YtMTcwMTE2NzU3MQ==")
HEYGEN_BASE_URL = "https://api.heygen.com/v1/video/generate"


def generate_heygen_video(photo_path: str, audio_path: str, output_path: str) -> str:
    headers = {
        "Authorization": f"Bearer {HEYGEN_API_KEY}"
    }

    files = {
        "avatar": open(photo_path, "rb"),
        "audio": open(audio_path, "rb")
    }

    print("[Heygen] Отправка запроса на генерацию видео...")
    response = requests.post(
        HEYGEN_BASE_URL,
        headers=headers,
        files=files
    )

    if response.status_code != 200:
        print(f"[Heygen] Ошибка: {response.status_code} — {response.text}")
        return ""

    video_id = response.json().get("video_id")
    print(f"[Heygen] Видео создается... ID: {video_id}")

    # Ожидание генерации
    video_url = ""
    for _ in range(30):
        status = requests.get(f"https://api.heygen.com/v1/video/status/{video_id}", headers=headers)
        data = status.json()
        if data.get("status") == "completed":
            video_url = data["video_url"]
            break
        time.sleep(2)

    if not video_url:
        print("[Heygen] Видео не готово.")
        return ""

    # Сохраняем видео
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "wb") as f:
        f.write(requests.get(video_url).content)

    print(f"[Heygen] Видео сохранено: {output_path}")
    return output_path
