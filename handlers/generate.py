# handlers/generate.py

import os
from uuid import uuid4
from pathlib import Path

from ai_services import generate_speech
from heygen_video_generation import generate_heygen_video
from utils.video_editor import add_subtitles_to_video, apply_format_overlay


def generate_reels(user_id, text, lang, format_type, with_subtitles):
    media_dir = Path(f"media/{user_id}")
    media_dir.mkdir(parents=True, exist_ok=True)

    avatar_path = media_dir / "avatar.jpg"
    voice_path = media_dir / "voice.mp3"
    raw_video_path = media_dir / f"raw_{uuid4().hex}.mp4"
    final_video_path = media_dir / f"reels_{uuid4().hex}.mp4"

    # Шаг 1: Генерация озвучки
    if not voice_path.exists():
        print("[AI] Генерация голоса...")
        success = generate_speech(text=text, language=lang, output_path=voice_path)
        if not success:
            print("[ERROR] Голос не сгенерирован")
            return None

    # Шаг 2: Генерация talking-аватара через Heygen
    print("[Heygen] Генерация talking-head видео...")
    result_path = generate_heygen_video(
        photo_path=avatar_path,
        audio_path=voice_path,
        output_path=raw_video_path
    )
    if not result_path or not os.path.exists(result_path):
        print("[ERROR] Видео не сгенерировано через Heygen")
        return None

    # Шаг 3: Добавление субтитров (если выбрано)
    if with_subtitles:
        print("[Subs] Добавление субтитров...")
        subtitled_path = media_dir / f"subtitled_{uuid4().hex}.mp4"
        result_path = add_subtitles_to_video(result_path, text, subtitled_path)

    # Шаг 4: Монтаж по формату (full, half, circle)
    print(f"[Format] Применение формата: {format_type}")
    formatted_path = apply_format_overlay(result_path, format_type, final_video_path)

    print(f"[DONE] Финальное видео сохранено в: {formatted_path}")
    return formatted_path
