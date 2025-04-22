import os
from pathlib import Path
from ai_services import generate_speech
from heygen_video_generation import generate_heygen_video
from utils.video_editor import combine_avatar_and_background


def generate_reels(user_id: int, text: str, lang: str, format_type: str, with_subtitles: bool = False) -> str:
    media_dir = Path(f"media/{user_id}")
    avatar_path = media_dir / "avatar.jpg"
    voice_path = media_dir / "voice.mp3"
    output_path = media_dir / "result.mp4"

    # Озвучка через OpenAI
    print("[GEN] Генерация голоса...")
    generate_speech(text=text, output_path=voice_path, language=lang)

    # Генерация видео с Heygen
    print("[GEN] Генерация видео Heygen...")
    avatar_video_path = generate_heygen_video(
        photo_path=str(avatar_path),
        voice_path=str(voice_path),
        user_id=user_id
    )

    if not avatar_video_path:
        print("[GEN] Ошибка генерации Heygen видео")
        return ""

    # Если формат - просто аватар, возвращаем как есть
    if format_type == "full":
        os.rename(avatar_video_path, output_path)
        return str(output_path)

    # Если формат 50/50 или круглый — нужен монтаж
    background_path = media_dir / "background.mp4"  # если понадобится вставка
    subtitles_path = media_dir / "subs.srt" if with_subtitles else None

    final_video_path = combine_avatar_and_background(
        avatar_video_path=avatar_video_path,
        background_video_path=background_path if background_path.exists() else None,
        format_type=format_type,
        subtitles_path=subtitles_path
    )

    if final_video_path:
        os.rename(final_video_path, output_path)
        return str(output_path)

    return ""
