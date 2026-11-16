# SPDX-License-Identifier: Apache-2.0
"""TrackIR "Enhanced" tables from opentrack's game list.

Run:  python -m unittest tests.test_trackir_tables -v
"""
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import trackir_tables as tt  # noqa: E402

HEADER = "No;Game Name;Game protocol;Supported since;Verified;By;INTERNATIONAL_ID;FTN_ID\n"


class TrackirTablesTests(unittest.TestCase):
    def test_star_citizen_table(self):
        # checked in game: Star Citizen (TrackIR id 3450) only moves the camera with this table
        tables = tt.load()
        self.assertEqual(tables[3450], bytes.fromhex("344ecef4a2b4c63e"))

    def test_key_decoding(self):
        self.assertEqual(tt.table_from_key("02CDF4CE4E343EC6B4A200"), bytes.fromhex("344ecef4a2b4c63e"))
        self.assertIsNone(tt.table_from_key("02CDF4"))
        self.assertIsNone(tt.table_from_key("zzCDF4CE4E343EC6B4A200"))

    def test_v160_and_zero_tables_are_skipped(self):
        text = HEADER + ("1;Old game;FreeTrack20;V160;;;13601;000121F172F35116A02100\n"
                         "2;Plain game;FreeTrack20;V170;;;13602;0000000000000000000000\n"
                         "3;Enhanced game;FreeTrack20;V170;;;3450;02CDF4CE4E343EC6B4A200\n"
                         "4;Broken line;FreeTrack20\n")
        self.assertEqual(tt.parse(text), {3450: bytes.fromhex("344ecef4a2b4c63e")})

    def test_reg_lines(self):
        self.assertEqual(tt.reg_lines({3450: bytes.fromhex("344ecef4a2b4c63e")}),
                         ['"3450"=hex:34,4e,ce,f4,a2,b4,c6,3e'])

    def test_missing_list_gives_no_tables(self):
        self.assertEqual(tt.load(paths=("/nonexistent/trackir_games.csv",)), {})


if __name__ == "__main__":
    unittest.main()
