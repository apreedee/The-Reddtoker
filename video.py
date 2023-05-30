from moviepy.editor import *
from moviepy.video.fx.all import *
import os

"""
This function finalises the video and makes it ready for uploading
"""


def finishing_video(assets_path, reddit_id, WIDTH, HEIGHT, PADDING, verbose):
    for i in os.scandir(f"./{assets_path}/temp/{reddit_id}/mp4"):
        x = f"./{assets_path}/temp/{reddit_id}/mp4/" + str(i.name)
    video_clip = VideoFileClip(x)
    audio_clip = AudioFileClip(f"./{assets_path}/temp/{reddit_id}/sound.mp3")
    if verbose:
        print(f"{video_clip.duration} - {audio_clip.duration}")

    video_clip = loop(video_clip, duration=audio_clip.duration)
    if verbose:
        print(f"{video_clip.duration}")
    video_clip = video_clip.set_audio(audio_clip)
    ratio = (1 / HEIGHT) * WIDTH
    height = video_clip.size
    if verbose:
        print(height)
        print("this")
    video_clip = video_clip.crop(
        width=(video_clip.size[1] * ratio),
        x1=(video_clip.size[0] - (video_clip.size[1] * ratio)) / 2,
    )

    video_and_images = [video_clip]
    current_time_in_video = 0
    for i in os.scandir(f"./{assets_path}/temp/{reddit_id}/png"):
        if i.name == "title.png":
            png_file_mp3_name = "audio_0.mp3"
            duration = AudioFileClip(
                f"./{assets_path}/temp/{reddit_id}/mp3/{png_file_mp3_name}"
            ).duration
            image = (
                ImageClip(f"./{assets_path}/temp/{reddit_id}/png/{i.name}")
                .set_start(current_time_in_video)
                .set_duration(duration)
                .set_position(("center", "center"))
            )
            if verbose:
                print(video_clip.size)
            image = image.resize(
                width=(video_clip.size[0] - (video_clip.size[0] * PADDING * 2))
            )
            current_time_in_video += duration
            # -- Finale --
            video_and_images.append(image)
    for i in os.scandir(f"./{assets_path}/temp/{reddit_id}/png"):
        if i.name != "title.png":
            png_file_mp3_name = str(
                int(i.name.replace(".png", "").replace("comment_", "")) + 1
            )
            png_file_mp3_name = f"audio_{png_file_mp3_name}.mp3"
            duration = AudioFileClip(
                f"./{assets_path}/temp/{reddit_id}/mp3/{png_file_mp3_name}"
            ).duration
            image = (
                ImageClip(f"./{assets_path}/temp/{reddit_id}/png/{i.name}")
                .set_start(current_time_in_video)
                .set_duration(duration)
                .set_position(("center", "center"))
            )
            image = image.resize(
                width=(video_clip.size[0] - (video_clip.size[0] * PADDING * 2))
            )
            if verbose:
                print(image.size)
            current_time_in_video += duration
            # -- Finale --
            video_and_images.append(image)
    video_clip = CompositeVideoClip(video_and_images).subclip(
        0, (AudioFileClip(f"./{assets_path}/temp/{reddit_id}/sound.mp3").duration)
    )
    video_clip.write_videofile(
        f"./{assets_path}/temp/{reddit_id}/video.mp4", preset="ultrafast", fps=30
    )
