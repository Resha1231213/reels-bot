import os
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
from pathlib import Path
from ai_services import generate_speech
from heygen_video_generation import generate_heygen_video

def generate_reels(user_id, text, lang, format_type, with_subtitles):
    user_folder = Path(f"media/{user_id}")
    avatar_path = user_folder / "avatar.jpg"
    audio_path = user_folder / "voice.mp3"
    result_path = user_folder / "reels_result.mp4"

    # Озвучка
    generate_speech(text=text, voice_id=lang, output_path=audio_path)

    # Генерация видео через Heygen
    generate_heygen_video(
        photo_path=str(avatar_path),
        audio_path=str(audio_path),
        output_path=str(result_path)
    )

    # Добавляем субтитры, если нужно
    if with_subtitles:
        result_path = add_subtitles_to_video(
            video_path=result_path,
            subtitles_text=text,
            output_path=user_folder / "reels_with_subs.mp4"
        )

    return str(result_path)

def add_subtitles_to_video(video_path, subtitles_text, output_path):
    video = VideoFileClip(str(video_path))

    subtitle = TextClip(
        txt=subtitles_text,
        fontsize=48,
        color='white',
        font="Arial-Bold",
        method='caption',
        size=(video.w * 0.9, None)
    ).set_duration(video.duration).set_position(('center', 'bottom'))

    final = CompositeVideoClip([video, subtitle])
    final.write_videofile(str(output_path), codec="libx264", audio_codec="aac")

    return output_path
