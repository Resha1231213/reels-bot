from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip, concatenate_videoclips
from pathlib import Path
import os

def assemble_reels_video(avatar_path: str, background_path: str = None, with_subs: bool = False,
                          subs_text: str = "", format_type: str = "full", output_path: str = "output/final_reel.mp4") -> str:
    """
    Собирает итоговое Reels-видео из аватара, обзора и субтитров.

    :param avatar_path: путь к видео с аватаром (Heygen)
    :param background_path: путь к видео-обзору (если формат 50/50 или круглый)
    :param with_subs: нужны ли субтитры
    :param subs_text: текст субтитров (если нужны)
    :param format_type: "full", "half", "circle"
    :param output_path: путь для сохранения
    :return: путь к собранному видео
    """
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    avatar = VideoFileClip(avatar_path).resize(height=1080)
    clips = []

    if format_type == "full":
        clips.append(avatar)

    elif format_type == "half" and background_path:
        background = VideoFileClip(background_path).resize(height=1080)
        avatar = avatar.resize(width=background.w // 2)
        background = background.resize(width=background.w // 2)
        final = CompositeVideoClip([
            background.set_position((0, 0)),
            avatar.set_position((background.w, 0))
        ], size=(background.w * 2, 1080))
        clips.append(final.set_duration(min(avatar.duration, background.duration)))

    elif format_type == "circle" and background_path:
        background = VideoFileClip(background_path).resize(height=1080)
        mask = avatar.to_mask().to_RGB().resize(height=400).margin(20, color=(0, 0, 0))
        avatar = avatar.set_mask(mask).resize(height=400)
        final = CompositeVideoClip([
            background,
            avatar.set_position((50, 50))
        ], size=(background.w, background.h))
        clips.append(final.set_duration(min(avatar.duration, background.duration)))

    if with_subs and subs_text:
        subtitle = TextClip(subs_text, fontsize=50, color='white', bg_color='black', font="Arial-Bold")
        subtitle = subtitle.set_duration(avatar.duration).set_position(("center", "bottom"))
        clips[0] = CompositeVideoClip([clips[0], subtitle])

    clips[0].write_videofile(output_path, fps=30, codec='libx264')
    return output_path
