import sqlite3
import unittest
from unittest.mock import patch, MagicMock, call

from application.functionalities import (
    fetch_foe_data, fetch_foe_detailed_data)
from scripts.common.db_writer import DbWriter


class test_fetches_foes(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        """Set up an in-memory SQLite database for testing"""
        con = sqlite3.connect("file::memory:?cache=shared", uri=True)
        con.execute("""
            CREATE TABLE foe (
                code TEXT,
                name TEXT)
            """)
        con.execute("""
            CREATE TABLE foe_detailed (
                code TEXT,
                name TEXT)
            """)
        con.executemany(
            """INSERT INTO foe(
                    code, name)
                VALUES(?, ?)""", [
                ("1230", "FOE 1"),
                ("0192", "FOE 2"),
                ("0000", "FOE 3"),
            ])
        con.executemany(
            """INSERT INTO foe_detailed(
                    code, name)
                VALUES(?, ?)""", [
                ("123022", "FOE 1"),
                ("019213", "FOE 2"),
                ("000000", "FOE 3"),
            ])
        con.commit()
        self.con = con
        self.cursor = self.con.cursor()

    @classmethod
    def tearDownClass(self):
        """Close the database connection after each test"""
        self.con.close()

    @patch.object(DbWriter, "DB_PATH", "file::memory:?cache=shared")
    def test_fetches_narrow_foe_in_right_format(self):
        results = fetch_foe_data()
        self.assertEqual(results, [
            ("FOE 1 (1230)", {"code": "1230", "name": "FOE 1"}),
            ("FOE 2 (0192)", {"code": "0192", "name": "FOE 2"}),
            ("FOE 3 (0000)", {"code": "0000", "name": "FOE 3"}),
        ])

    @patch.object(DbWriter, "DB_PATH", "file::memory:?cache=shared")
    def test_fetches_detailed_foe_in_right_format(self):
        results = fetch_foe_detailed_data()
        self.assertEqual(results, [
            ("FOE 1 (123022)", {"code": "123022", "name": "FOE 1"}),
            ("FOE 2 (019213)", {"code": "019213", "name": "FOE 2"}),
            ("FOE 3 (000000)", {"code": "000000", "name": "FOE 3"}),
        ])


if __name__ == '__main__':
    unittest.main()
