import sqlite3
import unittest
from unittest.mock import patch, MagicMock
from scripts.job_degree_scrapers.careers.database_helpers import (
    create_careers_table, update_job_listing_raw_with_career_id)


def get_table_columns(cursor, table_name):
    """Helper function to get the column definitions of a table"""
    cursor.execute(f"PRAGMA table_info({table_name})")
    return [(col[1], col[2]) for col in cursor.fetchall()]


@patch('builtins.print')
class test_careers_database_helpers(unittest.TestCase):
    @classmethod
    def setUp(self):
        """Set up an in-memory SQLite database for testing"""
        con = sqlite3.connect(":memory:")
        self.con = con
        self.cursor = self.con.cursor()

    @classmethod
    def tearDown(self):
        """Close the database connection after each test"""
        self.con.close()

    def test_creates_careers_table_with_right_schema(self, _mock_print):
        result = create_careers_table(self.con)
        self.assertTrue(result)

        columns = get_table_columns(self.cursor, "careers")
        expected_columns = [
            ('career_id', 'INTEGER'),
            ('career_name', 'TEXT'),
        ]
        self.assertEqual(columns, expected_columns)

    def test_creates_careers_table_succeeds_if_exists(self, _mock_print):
        create_careers_table(self.con)
        result = create_careers_table(self.con)
        self.assertTrue(result)

    def test_creates_careers_table_fails_on_operation_error(self, _mock_print):
        mock_con = MagicMock()
        mock_con.execute = MagicMock(side_effect=sqlite3.OperationalError())
        result = create_careers_table(mock_con)
        self.assertFalse(result)

    def test_creates_careers_table_throws_on_exception(self, _mock_print):
        mock_con = MagicMock()
        mock_con.execute = MagicMock(side_effect=Exception())

    def test_update_job_listing_with_new_column(self, _mock_print):
        self.con.execute("""
            CREATE TABLE job_listing_raw (
                job_id INTEGER PRIMARY KEY,
                job_title TEXT NOT NULL,
                location TEXT,
                salary TEXT,
                source TEXT
            )
            """)
        result = update_job_listing_raw_with_career_id(self.con)
        self.assertTrue(result)

        columns = get_table_columns(self.cursor, "job_listing_raw")
        expected_columns = [
            ('job_id', 'INTEGER'),
            ('job_title', 'TEXT'),
            ('location', 'TEXT'),
            ('salary', 'TEXT'),
            ('source', 'TEXT'),
            ('career_id', 'INTEGER')
        ]
        self.assertEqual(columns, expected_columns)

    def test_update_job_listing_fails_if_no_table(self, _mock_print):
        result = update_job_listing_raw_with_career_id(self.con)
        self.assertFalse(result)
