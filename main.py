import csv
import os
import time

from mp3_tagger import MP3File, VERSION_2, VERSION_BOTH

music_root = "E:\Music"
takeout_path = "Takeout\YouTube and YouTube Music\music-uploads"
music_path = os.path.join(music_root, takeout_path)

def cleanup(dirty_text):
    if isinstance(dirty_text, str):
        clean = dirty_text
        fix = [[":", "_"],
               ["'", "_"],
               ['"', "_"],
               ["/", "_"],
               [";", "_"], ]
        for a, b in fix:
            clean = clean.replace(a, b)
        return clean
    return dirty_text


start_time = time.time()
last_time = start_time
last_index = 0
mp3_files = [f for f in os.listdir(music_path) if os.path.isfile(os.path.join(music_path, f))]
keysv1 = ['artist', 'album', 'song', 'track', 'genre', 'year', 'comment']
keysv2 = ['artist', 'album', 'song', 'track', 'genre', 'year', 'band', 'comment', "composer", "copyright", "publisher", "url"]
keys_map = {'artist': 'artist', 'album': 'album', 'song': 'song', 'track': 'track', 'genre': 'genre', 'year': 'year', 'comment': 'comment', }
processed_files = []
ambiguous_files = []

with open(os.path.join(music_path, "music-uploads-metadata.csv"), "r", encoding='utf-8') as music_metadata_file:
    with open(os.path.join(music_path, "metadata_backup.csv"), "w", encoding='utf-8') as music_metadata_backup:
        music_metadata_reader = csv.reader(music_metadata_file)
        music_metadata = [md for md in music_metadata_reader]

        for md_index, metadata in enumerate(music_metadata):
            # print(metadata)
            title, album, artist, duration = metadata
            title = cleanup(title)
            album = cleanup(album)
            artist = cleanup(artist)
            mp3_filenames = [s for s in mp3_files if title[:40].lower() in s.lower()]  # Some titles got chopped to ~45 characters long.

            # Print Status every second
            if time.time() - last_time > 1:
                percent = (float(md_index) / len(music_metadata)) * 100.0
                bar = f"[{'#' * int(percent / 2.0)}{'-' * int((100 - percent) / 2.0)}]"
                guess = time.gmtime((len(music_metadata) - last_index) / (md_index - last_index))
                guess_time = time.strftime('%M:%S', guess)
                run_time = time.strftime('%M:%S', time.gmtime(time.time() - start_time))
                print(f"{bar} {md_index}/{len(music_metadata)} [{percent:0.1f}%] {md_index - last_index}/s {run_time}/{guess_time} ")
                last_time = time.time()
                last_index = md_index

            # Loop through all possible files for metadata
            for mp3_file in mp3_filenames:
                if mp3_file not in processed_files:
                    processed_files.append(mp3_file)

                    mp3_filename = os.path.join(music_path, mp3_file)
                    mp3 = MP3File(mp3_filename)

                    changed = False
                    tags = mp3.get_tags()
                    old_tags = {}
                    for tag_version in tags:
                        old_tags[tag_version] = {}
                        for key in tags[tag_version]:
                            old_tags[tag_version][key] = tags[tag_version][key]

                    # Clean up songs with junk data
                    if "ID3TagV1" in tags and "song" in tags["ID3TagV1"] and tags["ID3TagV1"]["song"]:
                        for key in tags["ID3TagV1"]:
                            if tags["ID3TagV1"][key] is not None and isinstance(tags["ID3TagV1"][key], str) and len(tags["ID3TagV1"][key]):
                                first_char = tags["ID3TagV1"][key][0]
                                if first_char * 4 in tags["ID3TagV1"][key]:  # Look for repeated characters. Clear data if found.
                                    tags["ID3TagV1"][key] = ""
                                    tags["ID3TagV2"][key] = ""
                                    changed = True

                    # Clean up trailing whitespace
                    for tag_version in tags:
                        for key in tags[tag_version]:
                            old = tags[tag_version][key]
                            if isinstance(old, str):
                                new = old.strip()
                                badchar = ["\x00", "\n", "\r"]
                                for bchar in badchar:
                                    new = new.replace(bchar, "")
                                if new != old:
                                    #print(f"{new}|")
                                    #print(f"{old}|")
                                    tags[tag_version][key] = new
                                    changed = True

                    # Clean up 'eng' added to comment by mp3-decode
                    for tag_version in tags:
                        if 'comment' in tags[tag_version] and tags[tag_version]["comment"] is not None:
                            while len(tags[tag_version]["comment"]) >= 3 and tags[tag_version]["comment"][:3] == "eng":
                                tags[tag_version]["comment"] = tags[tag_version]["comment"][3:]
                                changed = True
                            if tags[tag_version]["comment"] == "e":
                                tags[tag_version]["comment"] = ""

                    # If there is definitely only one file, set data to match Google
                    if len(mp3_filenames) == 1:
                        if "song" in tags["ID3TagV2"] and cleanup(tags["ID3TagV2"]["song"]) != title:
                            # print("Old Title", tags["ID3TagV2"]["song"])
                            # print("New Title", title)
                            tags["ID3TagV2"]["song"] = title
                        if "album" in tags["ID3TagV2"] and cleanup(tags["ID3TagV2"]["album"]) != album:
                            # print("Old album", tags["ID3TagV2"]["album"])
                            # print("New album", album)
                            tags["ID3TagV2"]["album"] = album
                        if "artist" in tags["ID3TagV2"] and cleanup(tags["ID3TagV2"]["artist"]) != artist:
                            # print("Old artist", tags["ID3TagV2"]["artist"])
                            # print("New artist", artist)
                            tags["ID3TagV2"]["artist"] = artist

                    # Copy data from V2 to V1
                    if "ID3TagV2" in tags and "ID3TagV1" in tags and tags["ID3TagV2"]:
                        for key in tags["ID3TagV2"]:
                            if key in keys_map:
                                if tags["ID3TagV2"][key]:
                                    if key in ['artist', 'album', 'song', 'comment']:
                                        old = tags["ID3TagV1"][keys_map[key]]
                                        new = tags["ID3TagV2"][key][:30]
                                        if old != new:
                                            changed = True
                                            tags["ID3TagV1"][keys_map[key]] = tags["ID3TagV2"][key]
                                    elif key == 'track':
                                        old = tags["ID3TagV1"][keys_map[key]]
                                        new = None
                                        try:
                                            new = int(tags["ID3TagV2"][key])
                                        except ValueError:
                                            pass
                                        if new is not None and old != new:
                                            changed = True
                                            tags["ID3TagV1"][keys_map[key]] = new

                    if changed:
                        # print(mp3_filename)
                        # print("old", old_tags)
                        # print("new", tags)
                        mp3.set_version(VERSION_BOTH)
                        for key in tags["ID3TagV2"]:
                            if tags["ID3TagV2"][key] is not None:
                                if key == "song":
                                    mp3.song = tags["ID3TagV2"][key]
                                elif key == "artist":
                                    mp3.artist = tags["ID3TagV2"][key]
                                elif key == "album":
                                    mp3.album = tags["ID3TagV2"][key]
                                elif key == "track":
                                    track_no = tags["ID3TagV2"][key]
                                    if len(track_no) > 2 and track_no[-2] == "/" and track_no[-1] == "0":
                                        track_no = track_no[0:-2]
                                    try:
                                        track_no = int(track_no)
                                        mp3.track = track_no
                                    except ValueError:
                                        mp3.set_version(VERSION_2)
                                        mp3.track = tags["ID3TagV2"][key]
                                        mp3.set_version(VERSION_BOTH)
                                elif key == "genre":
                                    mp3.set_version(VERSION_2)
                                    mp3.genre = tags["ID3TagV2"][key]
                                    mp3.set_version(VERSION_BOTH)
                                elif key == "year":
                                    mp3.year = tags["ID3TagV2"][key]
                                elif key == "comment":
                                    mp3.comment = tags["ID3TagV2"][key]
                                elif key == "band":
                                    mp3.band = tags["ID3TagV2"][key]
                                elif key == "url":
                                    mp3.url = tags["ID3TagV2"][key]
                                elif key == "copyright":
                                    mp3.copyright = tags["ID3TagV2"][key]
                                elif key == "composer":
                                    mp3.composer = tags["ID3TagV2"][key]
                                elif key == "publisher":
                                    mp3.publisher = tags["ID3TagV2"][key]
                        mp3.save()
                        pass
                    else:
                        # print("--------------")
                        # print(tags)
                        pass

                # If there is a single file:
                if len(mp3_filenames) == 1:
                    if artist and album:
                        artist_path = os.path.join(music_path, artist)
                        album_path = os.path.join(music_path, artist, album)

                        if not os.path.exists(artist_path):
                            os.mkdir(artist_path)
                        if not os.path.exists(album_path):
                            os.mkdir(album_path)
                        os.rename(os.path.join(music_path, mp3_file), os.path.join(album_path, mp3_file))
                else:
                    ambiguous_files.append(mp3_file)
                    dup_folder = os.path.join(music_path, "Duplicates")
                    if not os.path.exists(dup_folder):
                        os.mkdir(dup_folder)
                    if os.path.exists(os.path.join(music_path, mp3_file)):
                        os.rename(os.path.join(music_path, mp3_file), os.path.join(dup_folder, mp3_file))
                    # Do something with the duplicate files.
