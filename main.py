import praw
from screenshot_downloader import get_screenshots_of_reddit_posts
import configparser
from pathlib import Path
import os
from edit import edit_audios
from scheduler import seconds_to_time
import urllib
from praw.models import MoreComments
from pytube import YouTube
from audio import audio_transcript_calculator, audio_maker
from video import finishing_video
import time

"""
Seting up the config file and its data
"""
config = configparser.ConfigParser()
config.read("config.ini")

"""
Setting up a [PRAW] Reddit instance
"""

_start_time = time.time()

verbose = config["CONSOLE"].getboolean("Verbose")


def tic():
    global _start_time
    _start_time = time.time()


def tac():
    t_sec = round(time.time() - _start_time)
    (t_min, t_sec) = divmod(t_sec, 60)
    (t_hour, t_min) = divmod(t_min, 60)
    print("Time passed: {}hour:{}min:{}sec".format(t_hour, t_min, t_sec))


"""
This downloads and retrieves the video for the post
Whether on reddit or Youtube
"""


def download_video(dictionary: dict, path: str):
    if dictionary["video_source"] == "Reddit":
        # Getting info for video retrieval
        video_link = dictionary["link_for_video"].replace("?source=fallback", "")
        video_file_name = (
            f"./{path}/temp/"
            + dictionary["thread_id"]
            + "/"
            + "mp4/"
            + (video_link.split("/")[4])
            .replace("720", "360")
            .replace("1080", "360")
            .replace("480", "360")
        )

        # ! Make sure the reddit videos folder exists
        if verbose:
            print("Downloading Video")
        Path(f"{path}/temp/{dictionary['thread_id']}/mp4").mkdir(
            parents=True, exist_ok=True
        )
        if verbose:
            print("WAIT!!")
            print(video_link + " + " + video_file_name)
        urllib.request.urlretrieve(video_link, video_file_name)
        if verbose:
            print("VIDEO Downloaded")
    elif dictionary["video_source"] == "Youtube":
        if verbose:
            print("Downloading Video")
        link = dictionary["link_for_video"]
        yt = YouTube(link)
        yt = (
            yt.streams.filter(file_extension="mp4")
            .order_by("resolution")
            .desc()
            .first()
        )
        Path(f"{path}/temp/{dictionary['thread_id']}/mp4").mkdir(
            parents=True, exist_ok=True
        )
        if verbose:
            print("WAIT!!")
        yt.download(
            f"./{path}/temp/" + dictionary["thread_id"] + "/" + "mp4",
            filename="DASH_360.mp4",
        )
        if verbose:
            print("VIDEO Downloaded")


def main():
    """
    Setting up PRAW Reddit instance
    """
    reddit = praw.Reddit(
        client_id=config["GENERAL"]["REDDIT_CLIENT_ID"],
        client_secret=config["GENERAL"]["REDDIT_CLIENT_SECRET"],
        password=config["GENERAL"]["PASSWORD"],
        user_agent=config["GENERAL"]["USER_AGENT"],
        username=config["GENERAL"]["USERNAME"],
    )

    """
    Checking whether or not to print the status and values.
    """
    if verbose:
        print("Started PRAW")

    SUBREDDIT = config["GENERAL"]["SUBREDDIT"]

    """
    This Snippet takes all the previous videos (ie. folders) and
    arranges them into a list to not repeat them.
    """
    try:
        completed_Videos = os.scandir(f'./{config["GENERAL"]["ASSETS_PATH"]}/temp')
        temp_list = []
        for i in completed_Videos:
            temp_list.append(str(i).replace("<DirEntry '", "").replace("'>", ""))
        completed_Videos = temp_list
        if verbose:
            print(completed_Videos)
    except:
        if verbose:
            print("No previous videos detected")
        completed_Videos = []

    # Making an item which will later be used for screenshot retrieval
    dictionary = {}
    for submission in reddit.subreddit(SUBREDDIT).hot():
        # Filtering through the videos
        if (
            (
                config["GENERAL"].getboolean("OVER_18_ALLOWED")
                or (
                    (not config["GENERAL"].getboolean("OVER_18_ALLOWED"))
                    and (not submission.over_18)
                )
            )
            # Making sure no video which has already been completed is selected again.
            and submission.id not in completed_Videos
        ):
            if submission.is_video:
                if verbose:
                    print(f"Selected Video is {submission.id}")
                # Adding values to Dictionary
                dictionary["thread_url"] = f"https://reddit.com{submission.permalink}"
                dictionary["thread_title"] = submission.title
                dictionary["thread_id"] = submission.id
                dictionary["is_nsfw"] = submission.over_18
                dictionary["link_for_video"] = submission.media["reddit_video"][
                    "fallback_url"
                ]
                dictionary["video_source"] = "Reddit"
                dictionary["comments"] = []

                # Going through post comments
                for top_level_comment in submission.comments:
                    if isinstance(top_level_comment, MoreComments):
                        continue
                    if not top_level_comment.stickied:
                        if len(top_level_comment.body) <= int(2048):
                            if (
                                top_level_comment.author is not None
                            ):  # if errors occur with this change to if not.
                                dictionary["comments"].append(
                                    {
                                        "comment_body": top_level_comment.body,
                                        "comment_url": top_level_comment.permalink,
                                        "comment_id": top_level_comment.id,
                                    }
                                )
                time_totalled = 0
                dictionary["comments"].insert(
                    0, {"comment_body": dictionary["thread_title"]}
                )
                count_of_screenshots = len(dictionary["comments"])
                current_length = audio_transcript_calculator(
                    dictionary,
                    config["VOICEOVER"]["GENDER"],
                    config["VOICEOVER"]["RATE"],
                    config["VOICEOVER"]["VOLUME"],
                    config["GENERAL"]["ASSETS_PATH"],
                    dictionary["thread_id"],
                    verbose,
                )
                if verbose:
                    print(current_length)
                current_length = [current_length[-1]] + current_length[
                    : len(current_length) - 1
                ]
                if verbose:
                    print("Checked Comments.")

                # Downloading the video.
                download_video(dictionary, config["GENERAL"]["ASSETS_PATH"])

                max_screenshots_available_taken = 0
                if int(count_of_screenshots) == int(len(dictionary["comments"])):
                    max_screenshots_available_taken = True
                else:
                    max_screenshots_available_taken = False

                # This goes onto external function and implaments it.
                get_screenshots_of_reddit_posts(
                    dictionary,
                    count_of_screenshots,
                    int(config["VIDEO"]["VIDEO_WIDTH"]),
                    int(config["VIDEO"]["VIDEO_HEIGHT"]),
                    str(config["GENERAL"]["ASSETS_PATH"]) + "/temp",
                    config["GENERAL"]["USERNAME"],
                    config["GENERAL"]["PASSWORD"],
                    max_screenshots_available_taken,
                    verbose,
                )

                audio_maker(
                    dictionary,
                    config["GENERAL"]["ASSETS_PATH"] + "/temp",
                    dictionary["thread_title"],
                    count_of_screenshots,
                    dictionary["thread_id"],
                    verbose,
                )

                edit_audios(
                    dictionary["thread_id"],
                    config["GENERAL"]["ASSETS_PATH"],
                    verbose,
                )

                finishing_video(
                    config["GENERAL"]["ASSETS_PATH"],
                    dictionary["thread_id"],
                    int(config["VIDEO"]["VIDEO_WIDTH"]),
                    int(config["VIDEO"]["VIDEO_HEIGHT"]),
                    float(config["VIDEO"]["SCREENSHOT_DISPLAY_PADDING"]),
                    verbose,
                )

                break

            elif (
                submission.is_video == False
                and submission.subreddit.display_name == "videos"
            ):
                if verbose:
                    print(f"Selected Video is {submission.id}")
                # Adding values to Dictionary
                dictionary["thread_url"] = f"https://reddit.com{submission.permalink}"
                dictionary["thread_title"] = submission.title
                dictionary["thread_id"] = submission.id
                dictionary["is_nsfw"] = submission.over_18
                dictionary["link_for_video"] = submission.url_overridden_by_dest
                dictionary["video_source"] = "Youtube"
                dictionary["comments"] = []

                # Going through post comments
                for top_level_comment in submission.comments:
                    if isinstance(top_level_comment, MoreComments):
                        continue
                    if not top_level_comment.stickied:
                        if len(top_level_comment.body) <= int(2048):
                            if (
                                top_level_comment.author is not None
                            ):  # if errors occur with this change to if not.
                                dictionary["comments"].append(
                                    {
                                        "comment_body": top_level_comment.body,
                                        "comment_url": top_level_comment.permalink,
                                        "comment_id": top_level_comment.id,
                                    }
                                )
                time_totalled = 0
                dictionary["comments"].insert(
                    0, {"comment_body": dictionary["thread_title"]}
                )
                count_of_screenshots = len(dictionary["comments"])
                current_length = audio_transcript_calculator(
                    dictionary,
                    config["VOICEOVER"]["GENDER"],
                    config["VOICEOVER"]["RATE"],
                    config["VOICEOVER"]["VOLUME"],
                    config["GENERAL"]["ASSETS_PATH"],
                    dictionary["thread_id"],
                    verbose,
                )
                if verbose:
                    print(current_length)
                current_length = [current_length[-1]] + current_length[
                    : len(current_length) - 1
                ]
                if verbose:
                    print("Checked Comments.")

                # Downloading the video.
                download_video(dictionary, config["GENERAL"]["ASSETS_PATH"])

                max_screenshots_available_taken = 0
                if int(count_of_screenshots) == int(len(dictionary["comments"])):
                    max_screenshots_available_taken = True
                else:
                    max_screenshots_available_taken = False

                # This goes onto external function and implaments it.
                get_screenshots_of_reddit_posts(
                    dictionary,
                    count_of_screenshots,
                    int(config["VIDEO"]["VIDEO_WIDTH"]),
                    int(config["VIDEO"]["VIDEO_HEIGHT"]),
                    str(config["GENERAL"]["ASSETS_PATH"]) + "/temp",
                    config["GENERAL"]["USERNAME"],
                    config["GENERAL"]["PASSWORD"],
                    max_screenshots_available_taken,
                    verbose,
                )

                audio_maker(
                    dictionary,
                    config["GENERAL"]["ASSETS_PATH"] + "/temp",
                    dictionary["thread_title"],
                    count_of_screenshots,
                    dictionary["thread_id"],
                    verbose,
                )

                edit_audios(
                    dictionary["thread_id"],
                    config["GENERAL"]["ASSETS_PATH"],
                    verbose,
                )

                finishing_video(
                    config["GENERAL"]["ASSETS_PATH"],
                    dictionary["thread_id"],
                    int(config["VIDEO"]["VIDEO_WIDTH"]),
                    int(config["VIDEO"]["VIDEO_HEIGHT"]),
                    float(config["VIDEO"]["SCREENSHOT_DISPLAY_PADDING"]),
                    verbose,
                )

                break


def scheduler():
    seconds_minute = 60
    seconds_hour = seconds_minute * 60
    seconds_day = seconds_hour * 24

    nth_video = 0
    amount_of_videos = config["GENERAL"]["VIDEOS_PER_DAY"]
    always_true = True
    list_h = []
    for i in range(1, (amount_of_videos // 1)):
        x = (seconds_day // amount_of_videos) * nth_video
        y = seconds_to_time(x)
        list_h.append(y)
        nth_video += 1

    while always_true:
        z = time.localtime(time.time())
        if verbose:
            print([z.tm_hour, z.tm_min, z.tm_sec])
        if [z.tm_hour, z.tm_min, z.tm_sec] in list_h:
            tic()
            main()
            tac()
        time.sleep(0.5)


scheduler()

# to do this multiple times write for ($i=1; $i -le n; $i++) {python main.py} in cmd
