import time


def seconds_to_time(seconds):
    seconds_minute = 60
    seconds_hour = seconds_minute * 60
    seconds_day = seconds_hour * 24

    hour = int(((seconds % seconds_day) / seconds_hour) // 1)
    minutes = int(((seconds % seconds_hour) / seconds_minute) // 1)
    second = int(((seconds % seconds_minute) / 1) // 1)
    return [hour, minutes, second]
