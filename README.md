# Weather Report Station:
This repository contains code for the weather report station in the Northern Norway Science Center exhibition located in Tromsø.

Version: 0.1.1

## Hardware requirements:
The following hardware is recommended for running the application:
- A x86_64 computer with at least 2 GB RAM, a 2 GHz dual-core processor and a 25 GB SSD.
- A Wi-Fi connection, or preferably Ethernet for better reliability.
- A web-camera, with manual controls. We recommend the [Logitech StreamCam](https://www.logitech.com/no-no/products/webcams/streamcam.960-001297.html).
- A green screen background (or a blue screen if desired).
- Two monitors, with at least one having touch support. 
- Good light conditions, both on the background and subject.
- An external microphone, or just the inbuilt web-cam microphone.
- A mail server (e.g. a gmail account).

## Installation:
Follow the guide below to get the application running:
- Connect the camera, monitors, microphone and other hardware to the host computer.
- Install the latest [Ubuntu LTS](https://ubuntu.com/download/desktop) (22.04.1 is supported).
- Install necessary drivers for the touch screen and network adapters.

Once the machine has a fresh install of Ubuntu, run the following commands:
```
sudo apt install git
sudo apt install python3-pip
sudo pip install kivy
sudo pip install obsws-python
sudo apt-get install xclip xsel
sudo apt install flatpak
flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo
flatpak install flathub com.obsproject.Studio
flatpak run com.obsproject.Studio
reboot
```
Install the application with Git in the documents directory:
```
cd && cd Documents
git clone git@github.com:isakkjerstad/weather-report-station.git
```
Once installed, the program can be started by running:
```
cd weather-report-station
cd src
python3 main.py
```
However, four things have to be configured before the program will work correctly:
- The mail server must be configured in the "mail_sender_conf.py" file.
- Enable the OBS Web Server in "Menu->Tools->obs-websocket Settings". Set the OBS Web Server password in the "obs_manager_conf.py" file. The password and port number must match. The program (and OBS) will timeout after 45 seconds if not done correctly within time.
- Configure the camera and monitor settings in OBS. Overwrite the files in "obs_files/settings" to keep the changes on a restart of the application.
- Add backgrounds and thumbnails (see next section).

Note that OBS should ONLY be launched through the application. This applies especially when configuring profiles and scene collections. This is to ensure that the correct version of OBS is always being used. If the timeout prevents configuration, OBS may be initially launched with "flatpak run com.obsproject.Studio". The optional (but recommended) remaining tasks are as follows:
- Set up the machine to auto-login.
- Set up the application to start up on boot.
- Enable a watchdog, restarting the program on a crash.

Once done correctly, the machine should not need any user interaction on a reboot.

## Add new backgrounds:
To add a new background, do the following:
- Add a background video in the ''obs_files/backgrounds" directory. The file must be an ".mp4" video file.
- Add a thumbnail image in the "images/scenes" directory. The file must be an ".png" image file with the exact size of 320x180 pixels. The video and image file MUST have the same prefix name, i.e. a video named "background.mp4" must have a corresponding "background.png" thumbnail.

If a background does not have a correct thumbnail, it will cause an error. Likewise if a thumbnail does not have a background, it will also cause an error. In both cases, the program will fail to start. An incorrect thumbnail size will yield an error in the console, and may cause undefined behavior.

## Notes:
Below follows some useful information about the application:
- Video files are only temporary stored, and overwritten on each recording.
- Recording time can be changed by setting the "OBS_REC_TIME" in the main file.
- The recording file size must not exceed the max. allowed size by the mail server. File size is determined by factors like recording length, resolution, frame-rate and bit-rate. A too large file will prohibit the video from being sent, displaying an error to the user. If changing any of mentioned factors, please check the size of the "obs_files/recording/recording.mp4" file after a recording is done. Use a 3-4 MB margin.
- If the OBS Web Server is incorrectly configured the application will timeout after 45 seconds, and yield an error. This also applies if any other connection problems to OBS occur at startup.
- All "remove.me" files must be replaced with background videos or thumbnails. At least one pair of background assets (video + thumbnail) must exist for the application to operate correctly.
- The application supports Norwegian, English and German speaking users.

## Upcoming features:
The following features are planned, but not yet supported:
Feature | Implemented
:------------ | :-------------|
Virtual keyboard | :heavy_check_mark:
German language | :heavy_check_mark:
Installation script | :x:
OBS config. utility | :x:

Please report other missing features, requests and bugs as issues. New releases will be pushed as soon as possible. Only issues from the Northern Norway Science Center will be prioritized.
