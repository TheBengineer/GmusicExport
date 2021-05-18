import os
import pathlib
import tkinter as tk
from tkinter import filedialog

music_root = "D:\Music Sorter"
takeout_path = "Takeout\YouTube and YouTube Music\music-uploads"
music_path = os.path.join(music_root, takeout_path)
root = tk.Tk()
root.withdraw()

metadata_file = filedialog.askopenfilename(filetypes=[('.csvfiles', '.csv')], title='Select the music-uploads-metadata file in the music takeout folder.')
music_path = pathlib.Path(metadata_file).parent
print("asdf", metadata_file)
