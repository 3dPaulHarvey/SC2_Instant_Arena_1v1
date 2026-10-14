"""Protect the arena metadata while adding a second human lobby slot."""

from pathlib import Path
import struct
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import configure_players as lobby


def solo_template():
    current = lobby.read_mapinfo(lobby.DEFAULT_MAPINFO.read_bytes())
    by_pid = {player.pid: player for player in current.players}
    records = (by_pid[0].raw, by_pid[1].identity(1, 1, 0xFFFFFFFF), by_pid[15].raw)
    return current.prefix + struct.pack("<I", 3) + b"".join(records) + current.suffix


class MapInfoTests(unittest.TestCase):
    def test_playable_map_has_both_human_lobby_slots(self):
        # The conversion fixtures below also pass for a solo source map. Check
        # the real playable metadata so losing Player 2 cannot go unnoticed.
        payload = lobby.DEFAULT_MAPINFO.read_bytes()
        current = lobby.read_mapinfo(payload)
        self.assertEqual({player.pid: player.control for player in current.players},
                         {0: 3, 1: 1, 2: 1, 15: 4})
        self.assertEqual(lobby.configure_players(payload), payload)

    def test_second_human_and_colors_preserve_every_other_byte(self):
        before = lobby.read_mapinfo(solo_template())
        after = lobby.read_mapinfo(lobby.configure_players(solo_template()))
        self.assertEqual(before.prefix, after.prefix)
        self.assertEqual(before.suffix, after.suffix)
        self.assertEqual([(p.pid, p.control, p.color) for p in after.players],
                         [(0, 3, 0), (1, 1, 1), (2, 1, 2), (15, 4, 0)])
        self.assertEqual(before.players[0].raw, after.players[0].raw)
        self.assertEqual(before.players[-1].raw, after.players[-1].raw)
        self.assertEqual(before.players[1].raw[9:], after.players[1].raw[9:])
        self.assertEqual(before.players[1].raw[9:], after.players[2].raw[9:])
        self.assertEqual(len(before.prefix), 132)
        self.assertEqual(before.section_end, 205)
        self.assertEqual(after.section_end, 228)

    def test_configuration_is_idempotent(self):
        configured = lobby.configure_players(solo_template())
        self.assertEqual(configured, lobby.configure_players(configured))

    def test_unknown_trailing_bytes_survive(self):
        solo = solo_template()
        info = lobby.read_mapinfo(solo)
        suffix = bytes(range(52)) + b"future opaque metadata"
        payload = solo[:info.section_end] + suffix
        self.assertEqual(lobby.read_mapinfo(lobby.configure_players(payload)).suffix, suffix)

    def test_bad_metadata_is_rejected_before_file_changes(self):
        solo = solo_template()
        start = lobby.read_mapinfo(solo).section_start
        cases = {
            "magic": b"bad!" + solo[4:],
            "packed-version": solo[:4] + struct.pack("<I", 39) + solo[8:],
            "count": solo[:start] + struct.pack("<I", 17) + solo[start + 4:],
            "truncated-header": solo[:64],
            "truncated-record": solo[:180],
            "truncated-trailer": solo[:-1],
            "duplicate-id": solo[:start + 4 + 23] + b"\0" + solo[start + 4 + 24:],
            "wrong-user-controller": solo[:start + 4 + 24] + struct.pack("<I", 2) + solo[start + 4 + 28:],
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "MapInfo"
            for name, payload in cases.items():
                with self.subTest(name=name):
                    path.write_bytes(payload)
                    with self.assertRaises(lobby.MapInfoError):
                        lobby.configure_file(path)
                    self.assertEqual(path.read_bytes(), payload)
                    self.assertEqual(list(path.parent.iterdir()), [path])

    def test_file_configuration_changes_once(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "MapInfo"
            path.write_bytes(solo_template())
            self.assertTrue(lobby.configure_file(path))
            self.assertFalse(lobby.configure_file(path))


if __name__ == "__main__":
    unittest.main()
