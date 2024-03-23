import csv
import os
import time
import sys
import subprocess
from multiprocessing import Pool, cpu_count
import pathlib
import tkinter as tk
from tkinter import filedialog


def cleanup(dirty_text, replace_str="_"):
    if isinstance(dirty_text, str):
        clean = dirty_text.strip()
        fix = [[":", replace_str],
               ["'", replace_str],
               ['"', replace_str],
               ["/", replace_str],
               ["\\", replace_str],
               ["?", replace_str],
               ["*", replace_str],
               ["<", replace_str],
               [">", replace_str],
               ["|", replace_str],
               [";", replace_str], ]
        for a, b in fix:
            clean = clean.replace(a, b)
        return clean
    return dirty_text


def status(l_time, current_index, l_index, total, process_start_time):
    now = time.time()
    if now - l_time > .5:
        percent = (float(current_index) / total) * 100.0
        bar = f"[{'#' * int(percent / 2.0)}{'-' * int((100 - percent) / 2.0)}]"
        try:
            guess_seconds_total = (total / current_index) * (now - process_start_time)
            guess_seconds = guess_seconds_total - (now - process_start_time)
            guess = time.gmtime(guess_seconds)
        except ZeroDivisionError:
            guess = time.gmtime(0)
        guess_time = time.strftime('%M:%S', guess)
        run_time = time.strftime('%M:%S', time.gmtime(now - start_time))
        print(f"{bar} {current_index}/{total} [{percent:0.1f}%] {current_index - l_index}/s {run_time}/{guess_time} ")
        l_time = now
        l_index = current_index
    return l_time, l_index


def generate_files_dictionary(mp3_files, last_time, last_index, start_time, music_path=""):
    import mutagen
    from mutagen.mp3 import EasyMP3 as MP3
    # Generate a dictionary of all files
    files_dict = {filename: {"metadata": set(), "tags": {}, "duration": 0.0} for filename in mp3_files}

    # Load durations from all files.
    print("LOADING MP3 FILE METADATA AND DURATIONS")
    for md_index, mp3_filename in enumerate(mp3_files):
        last_time, last_index = status(last_time, md_index, last_index, len(mp3_files), start_time)
        try:
            mp3_data = MP3(os.path.join(music_path, mp3_filename))
            files_dict[mp3_filename]["duration"] = mp3_data.info.length
            tag_data = mp3_data.ID3.items(mp3_data)
            for field, data in tag_data:
                if len(data) > 0:
                    files_dict[mp3_filename]["tags"][field] = data[-1]
        except mutagen.mp3.HeaderNotFoundError:
            files_dict[mp3_filename]["duration"] = 0
            pass  # Skip non MP3 Files
    return files_dict


if __name__ == "__main__":  # Break out the main program
    core_count = max(cpu_count(), 1)
    pool = Pool(core_count)
    start_time = time.time()
    last_time = start_time - .1
    last_index = 0
    decision_matrix = {}
    decision_matrix_inv = {}

    subprocess.check_call([sys.executable, "-m", "pip", "install", "mutagen"])
    subprocess.check_call([sys.executable, "-m", "pip", "install", "numpy"])

    import mutagen
    from mutagen.mp3 import EasyMP3 as MP3

    from helpers import fuzzy2
    from unsort import unsort

    root = tk.Tk()
    root.withdraw()
    metadata_file = filedialog.askopenfilename(filetypes=[('.csvfiles', '.csv')],
                                               title='Select the music-uploads-metadata.csv file in the music takeout folder.')
    music_path = pathlib.Path(metadata_file).parent
    if not os.path.isfile(os.path.join(music_path, "music-uploads-metadata.csv")):
        print("COULD NOT FIND MUSIC")

    # Load Metadata
    with open(os.path.join(music_path, "music-uploads-metadata.csv"), "r", encoding='utf-8') as music_metadata_file:
        music_metadata_reader = csv.reader(music_metadata_file)
        headers = music_metadata_reader.__next__()
        music_metadata = {md_id: md for md_id, md in enumerate(music_metadata_reader)}

    print(f"MOVED {unsort(music_path)} FILES BACK TO MAIN FOLDER (IN CASE OF PREVIOUS RUNS)")
    # Fix mp3 files Google stripped .mp3 off. Get all files
    mp3_files = [f for f in os.listdir(music_path) if os.path.isfile(os.path.join(music_path, f)) and ".csv" not in f]
    for filename in mp3_files:
        if len(filename) < 4 or (filename[-4:].lower() != ".mp3" and filename[-4:] != ".csv"):
            os.rename(os.path.join(music_path, filename), os.path.join(music_path, f'{filename}.mp3'))
    mp3_files = [f for f in os.listdir(music_path) if os.path.isfile(os.path.join(music_path, f))]

    files_dict = generate_files_dictionary(mp3_files, last_time, last_index, start_time, music_path)

    print("BUILDING METADATA <-> FILE MATCH MATRIX")
    search_grid = {}
    for md_index in music_metadata:
        title, album, artist, duration = music_metadata[md_index]
        try:
            duration = float(duration)
        except ValueError:
            duration = 0
        search_title = cleanup(title).lower()

        if search_title not in search_grid:
            search_grid[search_title] = [md_index]
        else:
            search_grid[search_title].append(md_index)
        for word in search_title.split(" "):
            if len(word) > 3:
                if word not in search_grid:
                    search_grid[word] = [md_index]
                else:
                    search_grid[word].append(md_index)

    start_time = time.time()
    last_index = 0
    for file_number, filename in enumerate(mp3_files):
        for search_word in search_grid:
            if search_word in filename[:-4].lower():
                if len(search_grid[search_word]) == 1:
                    files_dict[filename]["metadata"].add(search_grid[search_word][0])
                elif len(search_grid[search_word]) > 1:
                    for md_index in search_grid[search_word]:
                        files_dict[filename]["metadata"].add(md_index)
        last_time, last_index = status(last_time, file_number, last_index, len(mp3_files), start_time)

    # Create Search Lookup matrix
    search_grid_inv = {}
    for filename in files_dict:
        for md_index in files_dict[filename]["metadata"]:
            if md_index not in search_grid_inv:
                search_grid_inv[md_index] = set()
            search_grid_inv[md_index].add(filename)

    print("POPULATING METADATA <-> FILE MATCH MATRIX")
    start_time = time.time()
    last_index = 0
    for md_number, md_index in enumerate(search_grid_inv):
        if len(search_grid_inv[md_index]) == 1:
            filename = search_grid_inv[md_index].pop()
            decision_matrix[md_index] = {filename: 100.0}
        elif len(search_grid_inv[md_index]) > 1:
            presorted = search_grid_inv[md_index]
            title, album, artist, duration = music_metadata[md_index]
            try:
                duration = float(duration)
            except ValueError:
                duration = 0

            to_fuzz = []

            for s in presorted:
                if "title" in files_dict[s]["tags"]:
                    to_fuzz.append([s, files_dict[s]["tags"]["title"], title])
                if "album" in files_dict[s]["tags"]:
                    to_fuzz.append([s, files_dict[s]["tags"]["album"], album])
                if "artist" in files_dict[s]["tags"]:
                    to_fuzz.append([s, files_dict[s]["tags"]["artist"], artist])

            fuzzed = pool.map(fuzzy2, to_fuzz)

            percentages = {s: 5 - abs((files_dict[s]["duration"] - duration)) for s in presorted if
                           files_dict[s]["duration"]}

            decisions = {}
            for filename in presorted:
                if filename not in decisions:
                    decisions[filename] = 1.0
                if filename in percentages:
                    decisions[filename] *= percentages[filename]
            for filename, ratio in fuzzed:
                decisions[filename] *= ratio
            decision_matrix[md_index] = decisions

        last_time, last_index = status(last_time, md_number, last_index, len(search_grid_inv), start_time)

    # Create inverse matrix
    for md_index in decision_matrix:
        for filename in decision_matrix[md_index]:
            if filename not in decision_matrix_inv:
                decision_matrix_inv[filename] = {}
            decision_matrix_inv[filename][md_index] = decision_matrix[md_index][filename]

    start_time = time.time()
    sorted_songs = 0
    last_index = 0
    print('SOLVING METADATA <-> FILE MATCH MATRIX')
    while 1:
        changed = False
        for md_index in decision_matrix:
            for filename in decision_matrix[md_index]:
                if md_index in decision_matrix and filename in decision_matrix[md_index]:
                    rating = decision_matrix[md_index][filename]
                    if rating == 100.0:
                        decision_matrix[md_index] = {filename: 100.0}
                        decision_matrix_inv[filename] = {md_index: 100.0}
                        sorted_songs += 1
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
                        decision_matrix[md_index] = {filename: 100.0}
                        decision_matrix_inv[filename] = {md_index: 100.0}
                        sorted_songs += 1
                        changed = True
                    # elif md_ratings[-1][1] == md_index and file_ratings[-1][1] == filename:  # MATCH
                    #     #decision_matrix[md_index] = {filename: 5.0}
                    #     #decision_matrix_inv[filename] = {md_index: 5.0}
                    #     pass
                last_time, last_index = status(last_time, sorted_songs, last_index, len(mp3_files), start_time)
        if not changed:
            break

    for md_index in decision_matrix:
        if len(decision_matrix[md_index]) == 1:
            filename = list(decision_matrix[md_index].keys())[0]
            if len(decision_matrix_inv[filename]) != 1:
                print(music_metadata[md_index][0], decision_matrix[md_index])

    print('MOVING FILES TO FOLDERS')
    # Process the files that the program was able to match
    start_time = time.time()
    processed_files = 0
    last_index = 0
    for file_number, filename in enumerate(mp3_files):
        artist = None
        album = None
        if filename in decision_matrix_inv:
            if len(list(decision_matrix_inv[filename].keys())) == 1:
                md_index = list(decision_matrix_inv[filename].keys())[0]
                title, album, artist, duration = music_metadata[md_index]
                tags = files_dict[filename]["tags"]
                changed = False

                # Print Status every second
                last_time, last_index = status(last_time, processed_files, last_index, len(mp3_files), start_time)

                # Update Mp3 with Google's tags
                if "title" not in tags or tags["title"] != title:
                    if len(title) > 3:
                        tags["title"] = title
                        changed = True
                if "album" not in tags or tags["album"] != album:
                    if len(album) > 3:
                        tags["album"] = album
                        changed = True
                if "artist" not in tags or tags["artist"] != artist:
                    if len(artist) > 3:
                        tags["artist"] = artist
                        changed = True

                if changed:
                    try:
                        mp3_data = MP3(os.path.join(music_path, filename))
                        for key in tags:
                            if key == "title":
                                mp3_data["title"] = tags[key]
                            elif key == "album":
                                mp3_data["album"] = tags[key]
                            elif key == "artist":
                                mp3_data["artist"] = tags[key]
                        mp3_data.save()
                    except mutagen.mp3.HeaderNotFoundError:
                        pass

        if "album" in files_dict[filename]["tags"]:
            album = files_dict[filename]["tags"]["album"]
        if "artist" in files_dict[filename]["tags"]:
            artist = files_dict[filename]["tags"]["artist"]

        if artist and album:
            artist_path = os.path.join(music_path, cleanup(artist, "")[50:])
            album_path = os.path.join(music_path, cleanup(artist, ""), cleanup(album, "")[50:])

            try:
                os.makedirs(album_path, exist_ok=True)
                os.rename(os.path.join(music_path, filename), os.path.join(album_path, filename))
            except Exception as e:
                print(e)
                # Catch file errors.
            processed_files += 1

    print(f'MOVED {processed_files} FILES TO FOLDERS')
    print("DONE")
