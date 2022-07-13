import unittest

from word_of_promise import Tracks


class TestTracks(unittest.TestCase):
    def setUp(self) -> None:
        self.t = Tracks()

    def test_all_tracks(self):
        tracks = self.t.tracks
        print(tracks)
