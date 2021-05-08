from mp3_tagger import MP3File, VERSION_BOTH, VERSION_2

# Create MP3File instance.
mp3 = MP3File("E:\\Music\\Takeout\\YouTube and YouTube Music\\music-uploads\\Silent Night(1).mp3")

tags = mp3.get_tags()
print(tags)
for tag_version in tags:
    for key in tags[tag_version]:
        tags[tag_version][key] = ""
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
del mp3

mp3 = MP3File("E:\\Music\\Takeout\\YouTube and YouTube Music\\music-uploads\\Seven Nation Army.mp3")

tags = mp3.get_tags()
print(tags)