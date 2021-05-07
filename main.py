from mp3_tagger import MP3File, VERSION_1, VERSION_2, VERSION_BOTH
import os
import csv

# Create MP3File instance.

music_root = "E:\Music"
takeout_path = "Takeout\YouTube and YouTube Music\music-uploads"
music_path = os.path.join(music_root, takeout_path)

with open(os.path.join(music_path, "music-uploads-metadata.csv"), "r", encoding='utf-8') as music_metadata_file:
    music_metadata = csv.reader(music_metadata_file)
    for metadata in music_metadata:
        #print(metadata)
        title, album, artist, duration = metadata
        if os.path.isfile(os.path.join(music_path, f"{title}.mp3")):
            #print(title)
            pass
        else:
            print(f"Failed {title}")

mp3 = MP3File(path_to_mp3)

# Get/set/del tags value.
alb = mp3.album
mp3.album = 'some title..'
del mp3.album
