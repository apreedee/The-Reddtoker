import sys
import subprocess

# implement pip as a subprocess:
subprocess.check_call([sys.executable, "-m", "pip", "install", "praw"])
subprocess.check_call([sys.executable, "-m", "pip", "install", "configparser"])
subprocess.check_call([sys.executable, "-m", "pip", "install", "pathlib"])
subprocess.check_call([sys.executable, "-m", "pip", "install", "pytube"])
subprocess.check_call([sys.executable, "-m", "pip", "install", "pyttsx3"])
subprocess.check_call([sys.executable, "-m", "pip", "install", "moviepy"])
subprocess.check_call([sys.executable, "-m", "pip", "install", "pytube"])
subprocess.check_call([sys.executable, "-m", "pip", "install", "typing"])
subprocess.check_call([sys.executable, "-m", "pip", "install", "regex"])
