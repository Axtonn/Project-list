import unittest
from unittest.mock import patch, MagicMock
import sqlite3

from scripts.job_degree_scrapers.requirements.database_helpers import (
    add_degree_requirement, career_id_from_raw_req, get_all_degrees,
    get_degree_requirements,  create_degree_requirements_table)


def get_table_columns(cursor, table_name):
    """Helper function to get the column definitions of a table"""
    cursor.execute(f"PRAGMA table_info({table_name})")
    return [(col[1], col[2]) for col in cursor.fetchall()]


@patch('builtins.print')
class test_degree_database_helpers(unittest.TestCase):
    @classmethod
    def setUp(self):
        """Set up an in-memory SQLite database for testing"""
        con = sqlite3.connect(":memory:")
        con.execute("""
            CREATE TABLE courses (
                course_id TEXT PRIMARY KEY,
                course_name TEXT,
                foe1_narrow_field TEXT)
            """)
        con.executemany(
            "INSERT INTO courses(course_name, foe1_narrow_field) VALUES (?, ?)",
            [("course1", "foe1"),
             ("course2", "foe1"),
             ("course3", "foe2"),])
        con.execute("""
            CREATE TABLE job_degree_requirements_raw (
                degree_id INTEGER PRIMARY KEY,
                degree TEXT,
                career INTEGER)
            """)
        con.executemany(
            "INSERT INTO job_degree_requirements_raw(degree, career) VALUES (?, ?)",
            [("degree1", 1),
             ("degree1", 2),
             ("degree2", 2),
             ("degree3", 3),])
        con.commit()
        self.con = con
        self.cursor = self.con.cursor()

    @classmethod
    def tearDown(self):
        """Close the database connection after each test"""
        self.con.close()

    def test_fetches_degrees_as_dict(self, _mock_print):
        # Ensure that `get_all_degrees` returns as a dictionary
        result = get_all_degrees(self.con)
        expected_result = {"foe1": ["course1", "course2"], "foe2": ["course3"]}
        self.assertEqual(result, expected_result)

    def test_fetches_degree_requirements_as_list(self, _mock_print):
        # Ensure that `get_all_degrees`` returns as a dictionary
        result = get_degree_requirements(self.con)
        self.assertEqual(result, [(1, "degree1", 1),
                                  (2, "degree1", 2),
                                  (3, "degree2", 2),
                                  (4, "degree3", 3),])

    def test_does_not_fetch_null(self, _mock_print):
        # Add database entries with null FOEs
        self.con.executemany(
            "INSERT INTO courses(course_name, foe1_narrow_field) VALUES (?, ?)",
            [("course4", None),
             ("course5", None),])
        self.con.commit()

        result = get_all_degrees(self.con)
        expected_result = {"foe1": ["course1", "course2"], "foe2": ["course3"]}
        self.assertEqual(result, expected_result)

    def test_uses_only_first_letters(self, _mock_print):
        # Test the edge case where several FOEs have the same code but not the
        # same name results in a single FOE in the output.
        self.con.executemany(
            "INSERT INTO courses(course_name, foe1_narrow_field) VALUES (?, ?)",
            [("course4", "foe1 - long foe1 name"),
             ("course5", "foe3: long foe3 name"),])
        self.con.commit()

        result = get_all_degrees(self.con)
        expected_result = {"foe1": ["course1", "course2", "course4"],
                           "foe2": ["course3"], "foe3": ["course5"]}
        self.assertEqual(result, expected_result)

    def test_uses_only_distinct_courses(self, _mock_print):
        # Test the edge case where several rows have the same course name for
        # the same FOE
        self.con.executemany(
            "INSERT INTO courses(course_name, foe1_narrow_field) VALUES (?, ?)",
            [("course1", "foe1 - long foe1 name"),
             ("course2", "foe2: long foe3 name"),])
        self.con.commit()

        result = get_all_degrees(self.con)
        expected_result = {"foe1": ["course1", "course2"],
                           "foe2": ["course3", "course2"], }
        self.assertEqual(result, expected_result)

    def test_creates_degree_requirements_table_with_right_schema(self, _mock_print):
        result = create_degree_requirements_table(self.con)
        self.assertTrue(result)

        columns = get_table_columns(self.cursor, "degree_requirements")
        expected_columns = [
            ('requirement_id', 'INTEGER'),
            ('foe_code', 'TEXT'),
            ('raw_requirement_id', 'INTEGER'),
            ('career_id', 'INTEGER'),
            ('matched_text', 'TEXT'),
            ('matched_weight', 'FLOAT')
        ]
        self.assertEqual(columns, expected_columns)

    def test_creates_degree_requirements_table_succeeds_if_exists(self, _mock_print):
        create_degree_requirements_table(self.con)
        result = create_degree_requirements_table(self.con)
        self.assertTrue(result)

    def test_creates_degree_requirements_table_fails_on_operation_error(self, _mock_print):
        mock_con = MagicMock()
        mock_con.execute = MagicMock(side_effect=sqlite3.OperationalError())
        result = create_degree_requirements_table(mock_con)
        self.assertFalse(result)

    def test_creates_degree_requirements_table_throws_on_exception(self, _mock_print):
        mock_con = MagicMock()
        mock_con.execute = MagicMock(side_effect=Exception())

        with self.assertRaises(Exception):
            create_degree_requirements_table(mock_con)

    def test_fetches_id_from_raw_req(self, _mock_print):
        self.con.execute("""
            CREATE TABLE careers (
                career_id INTEGER PRIMARY KEY,
                career_name TEXT)
            """)
        self.con.executemany(
            "INSERT INTO careers(career_name) VALUES (?)",
            [("career1",), ("career2",), ("career3",), ("career4",),])
        self.con.execute("""
            CREATE TABLE job_listing_raw (
                career_id INTEGER, 
                job_id INTEGER)
            """)
        self.con.executemany(
            "INSERT INTO job_listing_raw(career_id, job_id) VALUES (?, ?)",
            [(1, 1),
             (3, 2),
             (4, 3),])
        self.con.commit()

        result = career_id_from_raw_req(self.con, 2)
        self.assertEqual(result, (3,))

    def test_fetches_none_from_raw_req_on_error(self, _mock_print):
        mock_connection = MagicMock()
        mock_connection.cursor.return_value.execute = MagicMock(
            side_effect=sqlite3.OperationalError())
        result = career_id_from_raw_req(mock_connection, 2)
        self.assertIsNone(result)

    def test_adds_requirement(self, _mock_print):
        self.con.execute("""
            CREATE TABLE degree_requirements (
                foe_code TEXT,
                raw_requirement_id INTEGER,
                matched_text TEXT,
                matched_weight FLOAT,
                career_id INTEGER)
            """)

        result = add_degree_requirement(
            self.con,
            [("code", 2, "text", 0.5, 1,),
             ("code2", 3, "text", 0.1, 2,)])
        self.assertTrue(result)
        entries = self.con.execute("SELECT * from degree_requirements")
        self.assertEqual(entries.fetchall(),
                         [("code", 2, "text", 0.5, 1,),
                          ("code2", 3, "text", 0.1, 2,)])

    def test_does_not_add_requirement_on_error(self, _mock_print):
        mock_connection = MagicMock()
        mock_connection.cursor = MagicMock(
            side_effect=sqlite3.OperationalError())
        result = add_degree_requirement(mock_connection,
                                        ("code", 2, "text", 0.5, 1))
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()
