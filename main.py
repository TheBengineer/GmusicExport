import csv
import os
import time
import shelve

import mutagen
from mutagen.mp3 import EasyMP3 as MP3

from helpers import levenshtein_ratio_and_distance as fuzzy

from config import music_path


def cleanup(dirty_text):
    if isinstance(dirty_text, str):
        clean = dirty_text.strip()
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
decision_matrix = {}
decision_matrix_inv = {}
datastore = shelve.open('datastore', writeback=True)


# Load Metadata
with open(os.path.join(music_path, "music-uploads-metadata.csv"), "r", encoding='utf-8') as music_metadata_file:
    music_metadata_reader = csv.reader(music_metadata_file)
    headers = music_metadata_reader.__next__()
    music_metadata = {md_id: md for md_id, md in enumerate(music_metadata_reader)}

# Generate a dictionary of all files
files_dict = {filename: {"metadata": [], "tags": {}, "duration": 0.0} for filename in mp3_files}

# Load durations from all files.
print("LOADING FILE DURATIONS")
if "metadata" not in datastore:
    datastore["metadata"] = {}
    for md_index, mp3_filename in enumerate(mp3_files):
        now = time.time()
        if now - last_time > .5:
            percent = (float(md_index) / len(mp3_files)) * 100.0
            bar = f"[{'#' * int(percent / 2.0)}{'-' * int((100 - percent) / 2.0)}]"
            guess = time.gmtime(((len(mp3_files) - last_index) / (md_index - last_index)) / (now - last_time))
            guess_time = time.strftime('%M:%S', guess)
            run_time = time.strftime('%M:%S', time.gmtime(now - start_time))
            print(f"{bar} {md_index}/{len(mp3_files)} [{percent:0.1f}%] {md_index - last_index}/s {run_time}/{guess_time} ")
            last_time = time.time()
            last_index = md_index
            datastore.sync()
        try:
            mp3_data = MP3(os.path.join(music_path, mp3_filename))
            files_dict[mp3_filename]["duration"] = mp3_data.info.length
            tag_data = mp3_data.ID3.items(mp3_data)
            for field, data in tag_data:
                files_dict[mp3_filename]["tags"][field] = data[-1]
        except mutagen.mp3.HeaderNotFoundError:
            files_dict[mp3_filename]["duration"] = 0
            pass  # Skip non MP3 Files
        datastore["metadata"][mp3_filename] = [files_dict[mp3_filename]["duration"], files_dict[mp3_filename]["tags"]]
    datastore["metadata"] = datastore["metadata"]
    datastore.sync()
else:
    for filename in datastore['metadata']:
        duration, tags = datastore['metadata'][filename]
        if filename not in files_dict:
            files_dict[filename] = {"duration": 0.0, "tags": {}}
        files_dict[filename]["duration"] = duration

print("CREATING METADATA <-> FILE MATCH MATRIX")
# Match files to metadata
if "matrix_complete" not in datastore:
    if "matrix" not in datastore:
        datastore["matrix"] = {}
    start_time = time.time()
    for md_index in music_metadata:
        title, album, artist, duration = music_metadata[md_index]
        try:
            duration = float(duration)
        except ValueError:
            duration = 0
        search_title = cleanup(title).lower()

        presorted = set()
        for word in search_title.split(" "):
            if len(word) > 3:
                for s in mp3_files:
                    if word in s.lower():
                        presorted.add(s)
        if len(presorted) == 1:
            filename = presorted.pop()
            decision_matrix[md_index] = {filename: 5.0}
            datastore["matrix"][md_index] = {filename: 5.0}
        else:
            possible_files = {s: fuzzy(s[:-4].lower(), search_title[:30].lower(), ratio_calc=True) for s in presorted}
            title_score = {s: fuzzy(files_dict[s]["tags"]["title"].lower(), title.lower(), ratio_calc=True) for s in presorted if "title" in files_dict[s]["tags"]}
            album_score = {s: fuzzy(files_dict[s]["tags"]["album"].lower(), album.lower(), ratio_calc=True) for s in presorted if "album" in files_dict[s]["tags"]}
            artist_score = {s: fuzzy(files_dict[s]["tags"]["artist"].lower(), artist.lower(), ratio_calc=True) for s in presorted if "artist" in files_dict[s]["tags"]}

            # sorted_files = sorted([[a, b] for b, a in possible_files.items()])
            # print(title, possible_files[:min(3, len(possible_files))])
            if len(possible_files) < 1:
                asdf = True
            # durations = {files_dict[mp3_filename]["duration"]: mp3_filename for fuzz, mp3_filename in mp3_filenames}
            percentages = {mp3_filename: 5 - abs((files_dict[mp3_filename]["duration"] - duration)) for mp3_filename in possible_files if
                           files_dict[mp3_filename]["duration"]}
            # sorted_percent = sorted([[a, b] for b, a in percentages.items()])
            decisions = {}
            for filename in possible_files:
                decisions[filename] = possible_files[filename]
                if filename in percentages:
                    decisions[filename] *= percentages[filename]
                if filename in title_score:
                    decisions[filename] *= title_score[filename]
                if filename in album_score:
                    decisions[filename] *= album_score[filename]
                if filename in artist_score:
                    decisions[filename] *= artist_score[filename]

            for filename in decisions:
                decision_matrix[md_index] = decisions
                datastore["matrix"][md_index] = decisions
            # print(title, decision_matrix)
            # for fuzz, mp3_filename in mp3_filenames:
            #    files_dict[mp3_filename]["metadata"].append(metadata)
            now = time.time()
            if now - last_time > 1:
                percent = (float(md_index) / len(music_metadata)) * 100.0
                bar = f"[{'#' * int(percent / 2.0)}{'-' * int((100 - percent) / 2.0)}]"
                try:
                    guess = time.gmtime(((len(music_metadata) - last_index) / (md_index - last_index)) / (now - last_time))
                except ZeroDivisionError:
                    guess = time.gmtime(0)
                guess_time = time.strftime('%M:%S', guess)
                run_time = time.strftime('%M:%S', time.gmtime(now - start_time))
                print(f"{bar} {md_index}/{len(music_metadata)} [{percent:0.1f}%] {md_index - last_index}/s {run_time}/{guess_time} ")
                last_time = time.time()
                last_index = md_index
                datastore.sync()
    datastore["matrix_complete"] = True
else:
    for md_index in datastore["matrix"]:
        for filename in datastore["matrix"][md_index]:
            if md_index not in decision_matrix:
                decision_matrix[md_index] = {}
            decision_matrix[md_index][filename] = float(datastore["matrix"][md_index][filename])

#cells = []
for md_index in decision_matrix:
    for filename in decision_matrix[md_index]:
        if filename not in decision_matrix_inv:
            decision_matrix_inv[filename] = {}
        decision_matrix_inv[filename][md_index] = decision_matrix[md_index][filename]
        #cells.append([decision_matrix[md_index][filename], md_index, filename])

print('SOLVING MATCH MATRIX')
while 1:
    changed = False
    for md_index in decision_matrix:
        for filename in decision_matrix[md_index]:
            if md_index in decision_matrix and filename in decision_matrix[md_index]:
                rating = decision_matrix[md_index][filename]
                if rating == 5.0:
                    decision_matrix[md_index] = {filename: 5.0}
                    decision_matrix_inv[filename] = {md_index: 5.0}
                    continue
                md_ratings = []
                file_ratings = []
                for t_filename in decision_matrix[md_index]:
                    file_ratings.append([decision_matrix[md_index][t_filename], t_filename])
                for t_md_index in decision_matrix_inv[filename]:
                    md_ratings.append([decision_matrix_inv[filename][t_md_index], t_md_index])
                md_ratings.sort(reverse=True)
                file_ratings.sort(reverse=True)
                if md_ratings[0][1] == md_index and file_ratings[0][1] == filename:  # MATCH
                    decision_matrix[md_index] = {filename: 5.0}
                    decision_matrix_inv[filename] = {md_index: 5.0}
                # elif md_ratings[-1][1] == md_index and file_ratings[-1][1] == filename:  # MATCH
                #     #decision_matrix[md_index] = {filename: 5.0}
                #     #decision_matrix_inv[filename] = {md_index: 5.0}
                #     pass
    if not changed:
        break
for md_index in decision_matrix:
    if len(decision_matrix[md_index]) == 1:
        filename = list(decision_matrix[md_index].keys())[0]
        if len(decision_matrix_inv[filename]) != 1:
            print(music_metadata[md_index][0], decision_matrix[md_index])



# Process the files that the program was able to match
start_time = time.time()
processed_files = 0
for filename in decision_matrix_inv:
    if len(list(decision_matrix_inv[filename].keys())) == 1:
        md_index = list(decision_matrix_inv[filename].keys())[0]
        title, album, artist, duration = music_metadata[md_index]
        tags = files_dict[filename]["tags"]
        changed = False

        # Print Status every second
        now = time.time()
        if now - last_time > 1:
            percent = (float(processed_files) / len(music_metadata)) * 100.0
            bar = f"[{'#' * int(percent / 2.0)}{'-' * int((100 - percent) / 2.0)}]"
            guess = time.gmtime(((len(music_metadata) - last_index) / (md_index - last_index)) / (now - last_time))
            guess_time = time.strftime('%M:%S', guess)
            run_time = time.strftime('%M:%S', time.gmtime(now - start_time))
            print(f"{bar} {md_index}/{len(music_metadata)} [{percent:0.1f}%] {md_index - last_index}/s {run_time}/{guess_time} ")
            last_time = time.time()
            last_index = md_index

        # Update Mp3 with Google's tags
        if "title" in tags and tags["title"] != title:
            tags["title"] = title
            changed = True
        if "album" in tags and tags["album"] != album:
            tags["album"] = album
            changed = True
        if "artist" in tags and tags["artist"] != artist:
            tags["artist"] = album
            changed = True

        if changed:
            mp3_data = MP3(os.path.join(music_path, filename))
            for key in tags:
                mp3_data[key] = tags[title]
            mp3_data.save()

        if artist and album:
            artist_path = os.path.join(music_path, cleanup(artist))
            album_path = os.path.join(music_path, cleanup(artist), cleanup(album))

            if not os.path.exists(artist_path):
                os.mkdir(artist_path)
            if not os.path.exists(album_path):
                os.mkdir(album_path)
            os.rename(os.path.join(music_path, filename), os.path.join(album_path, filename))

    else:
        dup_folder = os.path.join(music_path, "Duplicates")
        if not os.path.exists(dup_folder):
            os.mkdir(dup_folder)
        if os.path.exists(os.path.join(music_path, filename)):
            os.rename(os.path.join(music_path, filename), os.path.join(dup_folder, filename))
        # Do something with the duplicate files.
