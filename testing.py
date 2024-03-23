import os
from main import generate_files_dictionary


mp3_files = []

for root, dirs, files in os.walk("Music/"):
    for file in files:
        if file.endswith(".mp3"):
            mp3_files.append(os.path.join(root, file))

print(mp3_files)