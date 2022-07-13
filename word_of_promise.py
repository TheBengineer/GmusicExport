
class Tracks:
    def __init__(self):
        tracks = []
        tracks += [f"Matthew {i}" for i in range(1, 12)]
        self.tracks = tracks

    def __str__(self):
        return  str(self.tracks)


if __name__ == "__main__":
    t = Tracks()
    print(t)