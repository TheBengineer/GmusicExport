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
            [f"Titus {i}" for i in range(1, 4)] +
            [f"Philemon {i}" for i in range(1, 2)] +
            [f"Hebrews {i}" for i in range(1, 10)])
        self.tracks = tracks

    def __str__(self):
        return str(self.tracks)


if __name__ == "__main__":
    t = Tracks()
    print(t)
