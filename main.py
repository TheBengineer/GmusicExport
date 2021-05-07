from mp3_tagger import MP3File, VERSION_1, VERSION_2, VERSION_BOTH
import os
import csv

# Create MP3File instance.

music_root = "E:\Music"
takeout_path = "Takeout\YouTube and YouTube Music\music-uploads"
music_path = os.path.join(music_root, takeout_path)


def cleanup(dirty_text):
    clean = dirty_text
    fix = [[":", "_"],
           ["'", "_"],
           ['"', "_"],
           ["/", "_"],
           [";", "_"], ]
    for a, b in fix:
        clean = clean.replace(a, b)
    return clean[:50]


mp3_files = [f for f in os.listdir(music_path) if os.path.isfile(os.path.join(music_path, f))]

with open(os.path.join(music_path, "music-uploads-metadata.csv"), "r", encoding='utf-8') as music_metadata_file:
    music_metadata = csv.reader(music_metadata_file)
    for metadata in music_metadata:
        # print(metadata)
        title, album, artist, duration = metadata
        title = cleanup(title)
        album = cleanup(album)
        artist = cleanup(artist)
        mp3_filenames = [s for s in mp3_files if title[:40] in s]
        if len(mp3_filenames) == 1:
            #print(f"Failed {title}, {mp3_filenames}")
            mp3_filename = os.path.join(music_path, mp3_filenames[0])
            mp3 = MP3File(mp3_filename)

            # Get/set/del tags value.
            tags = mp3.get_tags()
            if "ID3TagV1" in tags and "song" in tags["ID3TagV1"] and tags["ID3TagV1"]["song"] and ("UUUU" in tags["ID3TagV1"]["song"] or "ЄЄЄЄ" in tags["ID3TagV1"]["song"]):
                for tag_version in tags:
                    for key in tags[tag_version]:
                        tags[tag_version][key] = ""
                mp3.save()
            print(title)
            print(tags)
            print("------------------")
            #mp3.album = 'some title..'
            #del mp3.album




