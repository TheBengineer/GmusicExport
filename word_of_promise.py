import os

import mutagen
from mutagen.mp3 import EasyMP3 as MP3
from pydub import AudioSegment


class Tracks:
    def __init__(self):
        tracks = []
        tracks.append([f"Matthew {i}" for i in range(1, 12)])
        tracks.append([f"Matthew {i}" for i in range(12, 24)])
        tracks.append([f"Matthew {i}" for i in range(24, 29)] + [f"Mark {i}" for i in range(1, 4)])
        tracks.append([f"Mark {i}" for i in range(4, 12)])
        tracks.append([f"Mark {i}" for i in range(12, 17)] + [f"Luke {i}" for i in range(1, 5)])
        tracks.append([f"Luke {i}" for i in range(5, 14)])
        tracks.append([f"Luke {i}" for i in range(14, 22)])
        tracks.append([f"Luke {i}" for i in range(22, 25)] + [f"John {i}" for i in range(1, 7)])
        tracks.append([f"John {i}" for i in range(7, 17)])
        tracks.append([f"John {i}" for i in range(17, 22)] + [f"Acts {i}" for i in range(1, 8)])
        tracks.append([f"Acts {i}" for i in range(8, 19)])
        tracks.append([f"Acts {i}" for i in range(19, 29)])
        tracks.append([f"Romans {i}" for i in range(1, 17)])
        tracks.append([f"1 Corinthians {i}" for i in range(1, 17)])
        tracks.append([f"2 Corinthians {i}" for i in range(1, 14)] + [f"Galatians {i}" for i in range(1, 7)])
        tracks.append(
            [f"Ephesians {i}" for i in range(1, 7)] +
            [f"Philippians {i}" for i in range(1, 5)] +
            [f"Colossians {i}" for i in range(1, 5)] +
            [f"1 Thessalonians {i}" for i in range(1, 6)] +
            [f"2 Thessalonians {i}" for i in range(1, 4)])
        tracks.append(
            [f"1 Timothy {i}" for i in range(1, 7)] +
            [f"2 Timothy {i}" for i in range(1, 5)] +
            [f"Titus {i}" for i in range(1, 4)] +
            [f"Philemon {i}" for i in range(1, 2)] +
            [f"Hebrews {i}" for i in range(1, 10)])
        tracks.append(
            [f"Hebrews {i}" for i in range(10, 14)] +
            [f"James {i}" for i in range(1, 6)] +
            [f"1 Peter {i}" for i in range(1, 6)] +
            [f"2 Peter {i}" for i in range(1, 4)])
        tracks.append(
            [f"1 John {i}" for i in range(1, 6)] +
            [f"2 john {i}" for i in range(1, 2)] +
            [f"3 John {i}" for i in range(1, 2)] +
            [f"Jude {i}" for i in range(1, 2)] +
            [f"Revelation {i}" for i in range(1, 11)])
        tracks.append(
            [f"Revelation {i}" for i in range(11, 23)])
        self.tracks = tracks

    def __str__(self):
        return str(self.tracks)


class Metadata:
    def __init__(self):
        self.tracks = Tracks()
        self.music_path = "D:\\The Word of Promise"

    def process_all_files(self):
        for cd_id, cd_track in enumerate(self.tracks.tracks, start=1):
            for track_id, track in enumerate(cd_track, start=1):
                filename = self.get_wav_filename(cd_id, track_id)
                mp3_filename = self.generate_mp3_filename(cd_id, track)
                self.convert_to_mp3(filename, mp3_filename)
                self.set_file_metadata(mp3_filename, cd_id, track)

    def get_wav_filename(self, cd_id, track_id):
        return os.path.join(self.music_path, f"Disk {cd_id}\\{track_id:02} Track{track_id:02}.wav")

    def generate_mp3_filename(self, cd_id, track_name):
        return os.path.join(self.music_path, f"Disk {cd_id}\\{track_name}.mp3")

    @staticmethod
    def convert_to_mp3(filename, output_filename):
        wav_file = AudioSegment.from_file(filename)
        wav_file.export(output_filename, format="mp3")

    def set_file_metadata(self, filename, disk_id, title):
        album = "Word of Promise"
        artist = "The Word of Promise"
        year = "2020"
        disk = f"Disk {disk_id}"
        try:
            mp3_data = MP3(os.path.join(self.music_path, filename))
            mp3_data["title"] = title
            mp3_data["album"] = album
            mp3_data["artist"] = artist
            mp3_data["year"] = year
            mp3_data["disk"] = disk
            mp3_data.save()
        except mutagen.mp3.HeaderNotFoundError:
            pass


if __name__ == "__main__":
    t = Tracks()
    print(t)
    m = Metadata()
    m.process_all_files()
