# generate_video.py — генерация финального Reels

from ai_services import generate_speech, generate_talking_head
from pathlib import Path
import shutil
import os
import subprocess


def assemble_final_video(user_id: int, format: str = "half", with_subtitles: bool = True) -> str:
    base_dir = Path(f"media/{user_id}/output")
    base_dir.mkdir(parents=True, exist_ok=True)

    avatar_video = "media/temp/avatar_video.mp4"
    background = "assets/stock_sample.mp4"
    output_path = base_dir / "reels_final.mp4"

    if format == "half":
        # Ставим видео 50/50 (фон снизу, лицо сверху)
        cmd = [
            "ffmpeg",
            "-i", background,
            "-i", avatar_video,
            "-filter_complex",
            "[0:v]scale=720:640[bottom];[1:v]scale=720:640[top];[top][bottom]vstack=inputs=2[out]",
            "-map", "[out]",
            "-c:v", "libx264",
            "-y", str(output_path)
        ]
        subprocess.run(cmd)

    elif format == "full":
        shutil.copyfile(avatar_video, output_path)

    elif format == "circle":
        # Можно позже сделать наложение аватара в круге на фон
        shutil.copyfile(avatar_video, output_path)

    return str(output_path)


if __name__ == "__main__":
    user_id = 123456
    text = "Пример текста для Reels."
    lang = "ru"

    # Генерация речи
    print(f"[synthesize_speech] Язык: {lang}, текст: {text}")
    voice_path = generate_speech(text, voice_id="s3://voice-cloning-zero-shot/ru/vladimir.mp3")

    # Генерация видео-аватара
    print(f"[create_talking_avatar] Генерируем видео по фото: media/sample/photo.jpg и аудио: {voice_path}")
    avatar_video_path = generate_talking_head("media/sample/photo.jpg", voice_path)

    # Сборка Reels
    print(f"[assemble_final_video] Сборка Reels для user_id={user_id}, формат=half, субтитры=True")
    final_path = assemble_final_video(user_id=user_id, format="half", with_subtitles=True)

    print("✅ Готово! Видео сохранено в:", final_path)
