from moviepy.editor import *
import os

"""
This function takes in all the audio files and
only selects the ones it needs to make the final video.
"""


def delete_excess_files(assets_path, reddit_id, verbose):
    x = list(os.scandir(f"./{assets_path}/temp/{reddit_id}/mp3"))
    temp_x = []
    for i in x:
        if "audio_" in i.name:
            temp_x.append(i)
    x = temp_x
    z = []
    for i in x:
        if i.name == "audio_0.mp3":
            y = AudioFileClip(f"./{assets_path}/temp/{reddit_id}/mp3/" + str(i.name))
            z.append([y, y.duration, i.name])
        else:
            continue
    for i in x:
        if i.name == "audio_0.mp3":
            continue
        else:
            y = AudioFileClip(f"./{assets_path}/temp/{reddit_id}/mp3/" + str(i.name))
            z.append([y, y.duration, i.name])
    to_not_delete_list = []
    total_duration = 0
    MAXTIME = 60  # Chanhge this ! for customisability

    # right ordering before hand
    temp_list = list()  # -1 is to account for the title
    for i in z:
        if i[2] == "audio_0.mp3":
            temp_list.insert(0, i)
            if verbose:
                print(f"{i}" + "-" + f"{z}")
        else:
            continue
    for i in z:
        if i[2] == "audio_0.mp3":
            continue
        else:
            temp_list.insert(int(i[2].replace("audio_", "").replace(".mp3", "")), i)
            if verbose:
                print(f"{i}" + "-" + f"{z}")
    z = temp_list
    if verbose:
        print(z)
    del temp_list

    for i in z:
        if verbose:
            print(i)
        if i == z[0]:
            to_not_delete_list.insert(0, i)
            total_duration += i[1]
        elif i != z[0]:
            if total_duration + i[1] < MAXTIME:
                to_not_delete_list.append(i)
                total_duration += i[1]
                if verbose:
                    print(to_not_delete_list)
                    print(total_duration)

    return to_not_delete_list


"""
This function makes the final sound file
"""


def edit_audios(reddit_id: str, assets_path: str, verbose):
    y = delete_excess_files(assets_path, reddit_id, verbose)

    list_new_for_final_audio_track = []

    if verbose:
        print("here -1")
    for i in y:
        if i[2] == "audio_0.mp3":
            if verbose:
                print("here -2 " + i[2])
            audio_track = i[0]
            list_new_for_final_audio_track.insert(0, audio_track)

    for i in y:
        if i[2] != "audio_0.mp3":
            if verbose:
                print("here -3 " + i[2])
            audio_track = i[0]
            list_new_for_final_audio_track.append(audio_track)

    if verbose:
        print(list_new_for_final_audio_track)
    final_audio = concatenate_audioclips(list_new_for_final_audio_track)

    final_audio.write_audiofile(
        f"./{assets_path}/temp/{reddit_id}/sound.mp3", fps=44100
    )
