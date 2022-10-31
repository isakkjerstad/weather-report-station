'''
OBS configuration file.
'''

import os

def scene_destination() -> str:
    return os.path.expanduser("~") + "/.var/app/com.obsproject.Studio/config/obs-studio/basic/scenes/weather_scene.json"

def profile_destination_path() -> str:
    return os.path.expanduser("~") + "/.var/app/com.obsproject.Studio/config/obs-studio/basic/profiles/weather_profile"

# OBS Webserver settings.
HOST = "localhost"
PASSWORD = "<replace-me>"
PORT = 4455

# OBS manager settings.
RECORDING_PATH = "obs_files/recording"
BACKGROUND_DIR = "obs_files/backgrounds"
OBS_PROFILE_SRC = "obs_files/settings/blizzard-profile"
OBS_PROFILE_NAME = "blizzard-profile"
OBS_SCENE_COLLECTION_SRC = "obs_files/settings/weather-scene-collection"
OBS_SCENE_COLLECTION_NAME = "weather-scene-collection"
OBS_BACKGROUND_SOURCE_NAME = "background"
