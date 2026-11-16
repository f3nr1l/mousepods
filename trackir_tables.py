# SPDX-License-Identifier: Apache-2.0
"""TrackIR "Enhanced" encryption tables for the head-tracking bridge.

Some games (Star Citizen among them) ignore plain TrackIR data: they only accept frames encrypted
with an 8-byte table of their own. The DLL already handles this (native/npclient.c, LoadTable): it
reads the table from HKCU\\Software\\MousePods\\Table\\<TrackIR id> when the game registers its id.
bridge_install writes the table of every game in opentrack's list, so whatever game runs in the
prefix finds its own.

native/trackir_games.csv is opentrack's "settings/facetracknoir supported games.csv" (ISC);
the key decoding below follows opentrack's csv/csv.cpp.
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
CSV_NAME = "trackir_games.csv"
CSV_PATHS = (os.path.join(HERE, "native", CSV_NAME),)       # source tree and Flatpak (/app/share/mousepods)


def table_from_key(key):
    """FTN_ID column (11 bytes in hex) -> 8-byte table: bytes 5 4 3 2 9 8 7 6, as opentrack does."""
    if len(key) != 22:
        return None
    try:
        b = bytes.fromhex(key)
    except ValueError:
        return None
    return bytes((b[5], b[4], b[3], b[2], b[9], b[8], b[7], b[6]))


def parse(text):
    """{TrackIR id: table} for the games that need encryption."""
    tables = {}
    for line in text.splitlines()[1:]:
        col = line.rstrip("\r").split(";")
        if len(col) < 8 or not col[6].strip().isdigit():
            continue
        if col[3].strip() == "V160":             # opentrack: no encryption for V160 games
            continue
        table = table_from_key(col[7].strip())
        if table and any(table):
            tables.setdefault(int(col[6]), table)
    return tables


def load(paths=CSV_PATHS):
    """Tables from the first readable list; {} if none is found (the bridge then works as before)."""
    for path in paths:
        try:
            with open(path, encoding="utf-8", errors="replace") as f:
                return parse(f.read())
        except OSError:
            continue
    return {}


def reg_lines(tables):
    """user.reg lines, e.g. '"3450"=hex:34,4e,ce,f4,a2,b4,c6,3e'."""
    return ['"%d"=hex:%s' % (gid, ",".join("%02x" % c for c in t)) for gid, t in sorted(tables.items())]
