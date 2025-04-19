# handlers/generate.py

import os
from heygen_video_generation import generate_heygen_video
from ai_services import generate_speech
import subprocess
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
from pathlib import Path


def generate_reels(user_id: int, text: str, lang: str, format_type: str, with_subtitles: bool) -> str:
    media_dir = Path(f"media/{user_id}")
    media_dir.mkdir(parents=True, exist_ok=True)

    photo_path = media_dir / "avatar.jpg"
    output_path = media_dir / "final_video.mp4"
    temp_video_path = media_dir / "heygen_raw.mp4"

    print(f"[generate_reels] Пользователь: {user_id}")
    print(f"[generate_reels] Текст: {text}, Язык: {lang}, Формат: {format_type}, Субтитры: {with_subtitles}")

    # Генерация видео через Heygen
    generated_video = generate_heygen_video(
        photo_path=str(photo_path),
        script_text=text,
        output_path=str(temp_video_path),
        language=lang,
        voice_id="en_us_matthew" if lang == "en" else "ru_ekaterina"
    )

    if not generated_video or not Path(generated_video).exists():
        print("[generate_reels] Видео не сгенерировано!")
        return ""

    # Вставка субтитров (если нужно)
    if with_subtitles:
        final_video = add_subtitles(temp_video_path, text, output_path)
    else:
        os.rename(temp_video_path, output_path)
        final_video = output_path

    return str(final_video)


def add_subtitles(video_path: str, text: str, output_path: str) -> str:
    print(f"[subtitles] Добавление субтитров...")
    video = VideoFileClip(video_path)

    subtitle = TextClip(text, fontsize=40, color='white', bg_color='black', size=video.size, method='caption')
    subtitle = subtitle.set_position(('center', 'bottom')).set_duration(video.duration)

    final = CompositeVideoClip([video, subtitle])
    final.write_videofile(output_path, codec='libx264', audio_codec='aac')

    print(f"[subtitles] Субтитры добавлены в {output_path}")
    return output_path
