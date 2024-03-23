import os
import time
from main import generate_files_dictionary


mp3_files = []

for root, dirs, files in os.walk("Music/"):
    for file in files:
        if file.endswith(".mp3"):
            mp3_files.append(file)

print(mp3_files)
last_time = time.time()
start_time = time.time()
file_data = generate_files_dictionary(mp3_files, last_time, 0, start_time, "Music/")
print(file_data)