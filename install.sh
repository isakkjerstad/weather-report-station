#!/bin/bash

sudo apt install -y git
sudo apt install -y python3-pip
sudo pip install kivy
sudo pip install obsws-python
sudo apt-get install -y xclip xsel
sudo apt install -y flatpak
flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo
flatpak install flathub com.obsproject.Studio
flatpak run com.obsproject.Studio

cd src
python3 install_desktop_file.py

reboot