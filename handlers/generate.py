from pathlib import Path
import os
import uuid
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
from ai_services import generate_speech
from heygen_video_generation import generate_heygen_video


def generate_reels(user_id: int, text: str, lang: str, format_type: str, with_subtitles: bool) -> str:
    base_dir = Path("media") / str(user_id)
    avatar_path = base_dir / "avatar.jpg"
    voice_path = base_dir / "voice.mp3"
    output_path = base_dir / f"reel_{uuid.uuid4().hex}.mp4"

    success = generate_speech(text, lang, voice_path)
    if not success:
        print("[ERROR] Ошибка при генерации озвучки")
        return ""

    heygen_video_path = generate_heygen_video(str(avatar_path), str(voice_path), str(output_path))
    if not heygen_video_path:
        print("[ERROR] Ошибка при генерации видео с Heygen")
        return ""

    final_path = base_dir / f"final_{uuid.uuid4().hex}.mp4"

    try:
        clip = VideoFileClip(str(heygen_video_path))

        if format_type == "half":
            screen_width = 1080
            screen_height = 1920
            bg_clip = clip.resize(height=960)
            subtitle_area = TextClip(text, fontsize=40, color='white', bg_color='black', size=(1080, 960))
            subtitle_area = subtitle_area.set_duration(clip.duration).set_position(("center", "bottom"))
            final = CompositeVideoClip([bg_clip.set_position(("center", "top")), subtitle_area], size=(screen_width, screen_height))
        elif format_type == "circle":
            clip = clip.resize(height=720)
            final = CompositeVideoClip([clip.set_position("center")], size=(1080, 1920))
        else:
            final = clip

        if with_subtitles:
            subtitle = TextClip(text, fontsize=50, color='white', method='caption', size=final.size)
            subtitle = subtitle.set_duration(final.duration).set_position(("center", "bottom"))
            final = CompositeVideoClip([final, subtitle])

        final.write_videofile(str(final_path), codec="libx264", audio_codec="aac")
        return str(final_path)

    except Exception as e:
        print(f"[ERROR] Ошибка во время финального рендера: {e}")
        return ""
