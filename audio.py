import pyttsx3
import re
from pathlib import Path
from moviepy.editor import *
import os
import time
from math import ceil

engine = pyttsx3.init()

"""
This function filters the text to make it suitable for the audio making process
"""


def filtering_text(text):
    # removing links
    regex_urls = r"((http|https)\:\/\/)?[a-zA-Z0-9\.\/\?\:@\-_=#]+\.([a-zA-Z]){2,6}([a-zA-Z0-9\.\&\/\?\:@\-_=#])*"
    filtered_text = re.sub(regex_urls, " ", text)

    # replacing extra lines with spaces
    filtered_text = filtered_text.replace("\n", " ")

    # note: not removing apostrophes
    regex_expr = r"\s['|’]|['|’]\s|[\^_~@!&;#:\-%—“”‘\"%\*/{}\[\]\(\)\\|<>=+]"
    filtered_text = re.sub(regex_expr, " ", filtered_text)
    filtered_text = filtered_text.replace("+", "plus").replace("&", "and")

    # emoji removal
    filtered_text = re.sub(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F1E0-\U0001F1FF"  # flags (iOS)
        "]+",
        "",
        filtered_text,
    )

    return filtered_text


"""
This function estimates the duration of each comment
"""


def audio_transcript_calculator(
    texts: dict,
    gender: str,
    rate: str,
    volume: str,
    path: str,
    reddit_id: str,
    verbose,
):
    engine = pyttsx3.init()
    # Setting up the list for return
    times_list = []

    # Setting the engine to user preferences.
    engine.getProperty("voices")

    if gender == "male":
        engine.setProperty("voice", voices[0].id)
    elif gender == "female":
        engine.setProperty("voice", voices[1].id)

    engine.setProperty("rate", float(rate))
    engine.setProperty("volume", float(volume))

    # getting the rate of speech
    rate_of_speech = engine.getProperty("rate")

    # ! Make sure the reddit screenshots folder exists
    Path(f"./{path}/temp/{reddit_id}/mp3").mkdir(parents=True, exist_ok=True)

    for a in range(len(texts["comments"])):
        text = texts["comments"][a]["comment_body"]

        text = filtering_text(text)
        engine.save_to_file(text, f"./{path}/temp/{reddit_id}/mp3/{a}.mp3")
        engine.runAndWait()

        x = AudioFileClip(f"./{path}/temp/{reddit_id}/mp3/{a}.mp3")
        expected_time = int(x.duration)
        times_list.append(expected_time)
        x.close()
        if verbose:
            print(expected_time)

    return times_list


"""
This function makes each comment into a audio file.
These files are further used to make the final video.
"""


def audio_maker(
    texts: list,
    path: str,
    reddit_body: str,
    comment_quantity: int,
    reddit_id: str,
    verbose,
):
    text = ""
    list_of_text = []

    for part in range(comment_quantity):
        if verbose:
            print(part)
        list_of_text += [filtering_text(texts["comments"][part]["comment_body"]) + "\n"]

    list_of_text = [filtering_text(reddit_body) + "\n"] + list_of_text
    if verbose:
        print(list_of_text)

    Path(f"{path}/{reddit_id}/mp3").mkdir(parents=True, exist_ok=True)

    for i in list(range(len(list_of_text)))[1:]:
        x = f"audio_{i-1}" if i != 0 else "title"
        engine.save_to_file(
            filtering_text(list_of_text[i] + "\n"),
            f"{path}/{reddit_id}/mp3/{x}.mp3",
        )
        engine.runAndWait()
