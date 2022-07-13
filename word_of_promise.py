
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
        self.tracks = tracks







    def __str__(self):
        return str(self.tracks)


if __name__ == "__main__":
    t = Tracks()
    print(t)
