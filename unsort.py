import os

music_root = "E:\Music"
takeout_path = "Takeout\YouTube and YouTube Music\music-uploads"
music_path = os.path.join(music_root, takeout_path)

artist_folders = [f for f in os.listdir(music_path) if os.path.isdir(os.path.join(music_path, f))]

for artist_folder_name in artist_folders:
    artist_folder = os.path.join(music_path, artist_folder_name)
    album_folders = [f for f in os.listdir(artist_folder) if os.path.isdir(os.path.join(music_path, artist_folder, f))]
    for album_folder_name in album_folders:
        album_folder = os.path.join(artist_folder, album_folder_name)
        print(artist_folder, album_folder)
        mp3_files = [f for f in os.listdir(album_folder) if os.path.isfile(os.path.join(album_folder, f))]
        for mp3_filename in mp3_files:
            mp3_file = os.path.join(album_folder, mp3_filename)
            os.rename(mp3_file, os.path.join(music_path, mp3_filename))

