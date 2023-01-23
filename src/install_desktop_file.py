#!/usr/bin/python3

import os
import shutil

source_path = os.path.dirname(os.path.abspath(__file__))

desktop_file =  f"[Desktop Entry]" + f"\n"
desktop_file += f"Name=Weather Report Station" + f"\n"
desktop_file += f"Comment=Application for interactive green screen demonstration." + f"\n"
desktop_file += f"Exec={source_path + '/main.py'}" + f"\n"

if os.path.exists(source_path + '/images/icon.png'):
    print("Adding icon from '/images/icon.png'")
    desktop_file += f"Icon={source_path + '/images/icon.png'}" + f"\n"
else:
    print("Created desktop file without icon.")
    print("If you want an icon, add one at images/icon.png")

desktop_file += f"Type=Application" + f"\n"
desktop_file_destination = os.path.expanduser("~") + "/.local/share/applications/wrs.desktop"
dirname = os.path.dirname(desktop_file_destination)
os.makedirs(dirname, exist_ok=True)

with open(desktop_file_destination, 'w') as f:
    f.write(desktop_file)

print("\n")
print(desktop_file)
