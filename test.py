from mp3_tagger import MP3File, VERSION_BOTH, VERSION_2

# Create MP3File instance.
mp3 = MP3File("E:\\Music\\Takeout\\YouTube and YouTube Music\\music-uploads\\Seven Nation Army.mp3")

tags = mp3.get_tags()
print(tags)
for tag_version in tags:
    for key in tags[tag_version]:
        tags[tag_version][key] = ""
mp3.set_version(VERSION_BOTH)
mp3.album = ""
mp3.set_version(VERSION_2)
mp3.artist = "asdf"
mp3.set_version(VERSION_BOTH)
print(tags)

mp3.save()
del mp3

mp3 = MP3File("E:\\Music\\Takeout\\YouTube and YouTube Music\\music-uploads\\Seven Nation Army.mp3")

tags = mp3.get_tags()
print(tags)