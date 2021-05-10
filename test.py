mp3_files = ["asdff", "asdf.mp3", "D.mp3", "d"]

for filename in mp3_files:
    if len(filename) < 4 or (filename[-4:].lower() != ".mp3" and filename[-4:] != ".csv"):

        filename += ".mp3"
    print(filename)
