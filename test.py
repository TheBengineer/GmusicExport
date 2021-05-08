from mp3_tagger import MP3File, VERSION_BOTH

# Create MP3File instance.
mp3 = MP3File("E:\\Music\\Takeout\\YouTube and YouTube Music\\music-uploads\\This Is Berk.mp3")

print(mp3.get_tags())
alb = mp3.album
mp3.album = 'asdf'*50
mp3.set_version(VERSION_BOTH)
mp3.save()
