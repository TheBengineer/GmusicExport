from mp3_tagger import MP3File, VERSION_1, VERSION_2, VERSION_BOTH
import os
import csv
import time



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


start_time = time.time()
last_time = start_time
last_index = 0
mp3_files = [f for f in os.listdir(music_path) if os.path.isfile(os.path.join(music_path, f))]
keysv1 = ['artist', 'album', 'song', 'track', 'genre', 'year', 'comment']
keysv2 = ['artist', 'album', 'song', 'track', 'genre', 'year', 'band', 'comment', "composer", "copyright", "publisher", "url"]
keys_map = {'artist': 'artist', 'album': 'album', 'song': 'song', 'track': 'track', 'genre': 'genre', 'year': 'year', 'comment': 'comment', }
processed_files = []

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
            mp3_filenames = [s for s in mp3_files if title[:40] in s]  # Some titles got chopped to ~45 characters long.

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

                    if "ID3TagV1" in tags and "song" in tags["ID3TagV1"] and tags["ID3TagV1"]["song"]:
                        bad_data = ["UUUU", "ЄЄЄЄ", "ªªªª"]
                        fix_me = False
                        for bd in bad_data:
                            if bd in tags["ID3TagV1"]["song"]:
                                fix_me = True
                        if fix_me:
                            for tag_version in tags:
                                for key in tags[tag_version]:
                                    tags[tag_version][key] = ""
                            changed = True

                    # Clean up trailing whitespace
                    for tag_version in tags:
                        for key in tags[tag_version]:
                            old = tags[tag_version][key]
                            if isinstance(old, str):
                                new = old.strip()
                                if new != old:
                                    # print(f"{new}|")
                                    # print(f"{old}|")
                                    tags[tag_version][key] = new
                                    changed = True

                    # If there is definitely only one file
                    if len(mp3_filenames) == 1:
                        if "song" in tags["ID3TagV2"] and tags["ID3TagV2"]["song"] != title:
                            print(tags["ID3TagV2"]["song"])
                            print(title)
                        if "album" in tags["ID3TagV2"] and tags["ID3TagV2"]["album"] != album:
                            print(tags["ID3TagV2"]["album"])
                            print(album)
                        if "artist" in tags["ID3TagV2"] and tags["ID3TagV2"]["artist"] != artist:
                            print(tags["ID3TagV2"]["artist"])
                            print(artist)

                    # Copy data from V2 to V1
                    if "ID3TagV2" in tags and "ID3TagV1" in tags and tags["ID3TagV2"]:
                        for key in tags["ID3TagV2"]:
                            if key in keys_map:
                                tags["ID3TagV1"][keys_map[key]] = tags["ID3TagV2"][key]
                                changed = True

                    if changed:
                        # print("old", old_tags)
                        # print("new", tags)
                        # mp3.save()

                        pass
                    else:
                        # print("--------------")
                        # print(tags)
                        pass

            if len(mp3_filenames) == 1:
                pass

                # TODO determine if use V1 or V2
                # print(title)
                # print(tags)
                # print("------------------")
                # mp3.album = 'some title..'
                # del mp3.album
            else:
                pass
                # Do something with the duplicate files.
            break
