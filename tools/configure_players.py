"""Configure two human slots in the arena's editable version-34 MapInfo.

This deliberately does not support packed maps or newer MapInfo versions. Only
the player section is rewritten; the header and unknown trailing data survive
byte for byte. Run this once for the component-folder map, then save/publish it
with the StarCraft II editor.

The v34 player layout follows the MapInfo/MapInfoPlayer decoder in
https://github.com/ggtracker/sc2reader/blob/master/sc2reader/objects.py.
"""

from dataclasses import dataclass
from pathlib import Path
import argparse
import os
import struct
import tempfile


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MAPINFO = ROOT / "src/InstantArena_Basic.SC2Map/MapInfo"
SUPPORTED_VERSION = 34


class MapInfoError(ValueError):
    """The metadata is malformed or outside the supported arena template."""


class _Reader:
    def __init__(self, payload):
        self.payload = payload
        self.offset = 0

    def take(self, size):
        if size < 0 or self.offset + size > len(self.payload):
            raise MapInfoError("Truncated MapInfo metadata.")
        value = self.payload[self.offset:self.offset + size]
        self.offset += size
        return value

    def integer(self, size=4):
        return int.from_bytes(self.take(size), "little")

    def cstring(self):
        end = self.payload.find(b"\0", self.offset)
        if end < 0:
            raise MapInfoError("Unterminated MapInfo string.")
        raw = self.take(end - self.offset + 1)
        try:
            return raw[:-1].decode("utf-8")
        except UnicodeDecodeError as error:
            raise MapInfoError("Invalid UTF-8 in MapInfo string.") from error


@dataclass(frozen=True)
class Player:
    pid: int
    control: int
    color: int
    race: str
    unknown: int
    start_point: int
    ai: int
    decal: str
    raw: bytes

    def identity(self, pid, control, color):
        # All other fields, including the original string encoding, survive.
        return struct.pack("<BII", pid, control, color) + self.raw[9:]


@dataclass(frozen=True)
class MapInfo:
    prefix: bytes
    players: tuple
    suffix: bytes

    @property
    def section_start(self):
        return len(self.prefix)

    @property
    def section_end(self):
        return len(self.prefix) + 4 + sum(len(player.raw) for player in self.players)


def read_mapinfo(payload):
    """Read only the known v34 header and records, retaining the opaque suffix."""
    reader = _Reader(payload)
    if reader.take(4) != b"IpaM":
        raise MapInfoError("Invalid MapInfo magic.")
    if reader.integer() != SUPPORTED_VERSION:
        raise MapInfoError("Only editable MapInfo version 34 is supported.")
    reader.take(8)  # Editor version and an unknown header field.
    width, height = reader.integer(), reader.integer()
    if not (0 < width <= 4096 and 0 < height <= 4096):
        raise MapInfoError("Invalid MapInfo dimensions.")
    for _ in range(2):
        preview_type = reader.integer()
        if preview_type not in (0, 1, 2):
            raise MapInfoError("Invalid MapInfo preview type.")
        if preview_type == 2:
            reader.cstring()
    reader.cstring()  # Additional preview setting introduced in v31.
    reader.take(8)  # Unknown v31 setting and unknown general setting.
    reader.cstring()  # Fog type.
    reader.cstring()  # Tileset.
    reader.take(20)  # Camera bounds and base height.
    if reader.integer() not in (0, 1):
        raise MapInfoError("Invalid loading-screen type.")
    reader.cstring()  # Loading-screen image.
    reader.take(reader.integer(2))  # Length-prefixed loading-screen string.
    reader.take(32)  # Scaling, text positioning, flags, and an unknown setting.
    reader.take(8 + 9 + 4)  # Version-specific unknown fields (v25/v31/v32).

    section_start = reader.offset
    count = reader.integer()
    if not (1 <= count <= 16):
        raise MapInfoError("Invalid player count.")
    players = []
    for _ in range(count):
        start = reader.offset
        pid, control, color = reader.integer(1), reader.integer(), reader.integer()
        race = reader.cstring()
        unknown, start_point, ai = reader.integer(), reader.integer(), reader.integer()
        decal = reader.cstring()
        if pid > 15 or control > 4 or (color > 15 and color != 0xFFFFFFFF):
            raise MapInfoError("Invalid player record.")
        players.append(Player(pid, control, color, race, unknown, start_point,
                              ai, decal, payload[start:reader.offset]))
    if len({player.pid for player in players}) != count:
        raise MapInfoError("Duplicate player identifiers.")
    suffix = payload[reader.offset:]
    # This arena template has 52 trailing bytes. Their meaning is deliberately
    # left opaque, but a missing/truncated trailer must never be rewritten.
    if len(suffix) < 52:
        raise MapInfoError("Missing or truncated arena MapInfo trailer.")
    return MapInfo(payload[:section_start], tuple(players), suffix)


def configure_players(payload):
    """Return an idempotent two-human configuration without changing other data."""
    original = read_mapinfo(payload)
    players = {player.pid: player for player in original.players}
    if set(players) not in ({0, 1, 15}, {0, 1, 2, 15}):
        raise MapInfoError("Unexpected player slots; refusing to replace this map's layout.")
    if players[0].control != 3 or players[1].control != 1 or players[15].control != 4:
        raise MapInfoError("Expected Neutral 0, User 1, and Hostile 15.")
    if 2 in players and players[2].control != 1:
        raise MapInfoError("Player 2 already exists with a non-user controller.")
    second = players.get(2, players[1])
    records = (players[0].raw, players[1].identity(1, 1, 1),
               second.identity(2, 1, 2), players[15].raw)
    configured = original.prefix + struct.pack("<I", 4) + b"".join(records) + original.suffix
    verified = read_mapinfo(configured)
    if verified.prefix != original.prefix or verified.suffix != original.suffix:
        raise MapInfoError("MapInfo data outside the player section changed.")
    return configured


def configure_file(path=DEFAULT_MAPINFO):
    """Validate completely before replacing the component-folder metadata."""
    path = Path(path)
    original = path.read_bytes()
    configured = configure_players(original)
    if configured == original:
        return False
    temporary_path = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, prefix=".MapInfo-", delete=False) as temporary:
            temporary_path = Path(temporary.name)
            temporary.write(configured)
        os.replace(temporary_path, path)
    finally:
        if temporary_path is not None and temporary_path.exists():
            temporary_path.unlink()
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="?", type=Path, default=DEFAULT_MAPINFO)
    arguments = parser.parse_args()
    changed = configure_file(arguments.path)
    print("Configured Player 1 (red) and Player 2 (blue)." if changed else "Two human players already configured.")
