import tkinter as tk
from tkinter import filedialog

root = tk.Tk()
root.withdraw()

file_path = filedialog.askopenfilename(filetypes=[('.csvfiles', '.csv')], title='Select the music-uploads-metadata file in the music takeout folder.')

mp3_files = ["asdff", "asdf.mp3", "D.mp3", "d"]

for filename in mp3_files:
    if len(filename) < 4 or (filename[-4:].lower() != ".mp3" and filename[-4:] != ".csv"):
        filename += ".mp3"
    print(filename)
