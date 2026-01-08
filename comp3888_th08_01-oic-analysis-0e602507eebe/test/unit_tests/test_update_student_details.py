import sqlite3
import unittest
from unittest.mock import patch

from application.display_degrees import update_student_details
from scripts.common.db_writer import DbWriter


class test_update_student_details(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        """Set up an in-memory SQLite database for testing"""
        con = sqlite3.connect("file::memory:?cache=shared")
        con.execute("""
            CREATE TABLE students (
                student_id INTEGER PRIMARY KEY,
                given_name TEXT,
                surname TEXT)
            """)
        con.executemany(
            """INSERT INTO students(
                    given_name, surname
                ) VALUES(?, ?)""",
            [
                ("John", "Smith"),
                ("Anne", "Li"),
                ("Jane", "Doe")
            ])
        con.execute("""
            CREATE TABLE grades (
                student_id INTEGER,
                score FLOAT, 
                exam_id TEXT)
            """)
        con.executemany(
            """INSERT INTO grades(
                    student_id, score, exam_id
                ) VALUES(?, ?, ?)""",
            [
                (1, 85.5, "ATAR"),
                (2, 650, "GAOKAO"),
                (3, 44, "IBD"),
            ])
        con.commit()
        self.con = con
        self.cursor = self.con.cursor()

    @classmethod
    def tearDownClass(self):
        """Close the database connection after each test"""
        self.con.close()

    @patch.object(DbWriter, "DB_PATH", "file::memory:?cache=shared")
    def test_returns_dictionary_of_values(self):
        result = update_student_details({"student_id": 1})
        self.assertEqual(result, {
            "name": "John Smith",
            "grade": 85.5,
            "exam_type": "ATAR",
            "id": 1
        })

    @patch.object(DbWriter, "DB_PATH", "file::memory:?cache=shared")
    def test_none_if_no_student_id(self):
        result = update_student_details({"other_json_data": []})
        self.assertIsNone(result)

    @patch.object(DbWriter, "DB_PATH", "file::memory:?cache=shared")
    def test_none_if_no_student_id(self):
        result = update_student_details({"other_json_data": []})
        self.assertIsNone(result)
