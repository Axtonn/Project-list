import unittest
import sqlite3
import pandas as pd
from unittest.mock import patch

from scripts.datagov_script.datagov_script import (
    create_institutions_table,
    create_course_locations_table,
    create_locations_table,
    create_courses_table,
    import_csv_to_sqlite
)

@unittest.skip('Skipping the unit tests due to pipeline environment')
class TestDataGovScript(unittest.TestCase):

    def setUp(self):
        """Set up an in-memory SQLite database for testing"""
        self.con = sqlite3.connect(":memory:")
        self.cursor = self.con.cursor()

    def tearDown(self):
        """Close the database connection after each test"""
        self.con.close()

    def get_table_columns(self, table_name):
        """Helper function to get the column definitions of a table"""
        self.cursor.execute(f"PRAGMA table_info({table_name})")
        # Returns column name and type
        return [(col[1], col[2]) for col in self.cursor.fetchall()]

    # Test for Institutions table existence and correct columns
    def test_create_institutions_table(self):
        """Test that the institutions table is created with the correct schema"""
        create_institutions_table(self.con)
        columns = self.get_table_columns('institutions')
        expected_columns = [
            ('institution_id', 'TEXT'),
            ('institution_name', 'TEXT'),
            ('institution_type', 'TEXT')
        ]
        self.assertEqual(columns, expected_columns,
                         "Institutions table schema is incorrect")

    # Test for Course Locations table existence and correct columns
    def test_create_course_locations_table(self):
        """Test that the course_locations table is created with the correct schema"""
        create_course_locations_table(self.con)
        columns = self.get_table_columns('course_locations')
        expected_columns = [
            ('cl_id', 'INTEGER'),
            ('course_id', 'TEXT'),
            ('location_name', 'TEXT'),
            ('city', 'TEXT'),
            ('state', 'TEXT')
        ]
        self.assertEqual(columns, expected_columns,
                         "Course Locations table schema is incorrect")

    # Test for Locations table existence and correct columns
    def test_create_locations_table(self):
        """Test that the locations table is created with the correct schema"""
        create_locations_table(self.con)
        columns = self.get_table_columns('locations')
        expected_columns = [
            ('l_id', 'INTEGER'),
            ('location_name', 'TEXT'),
            ('address_line_1', 'TEXT'),
            ('city', 'TEXT'),
            ('state', 'TEXT'),
            ('postcode', 'INTEGER')
        ]
        self.assertEqual(columns, expected_columns,
                         "Locations table schema is incorrect")

    # Test for Courses table existence and correct columns
    def test_create_courses_table(self):
        """Test that the courses table is created with the correct schema"""
        create_courses_table(self.con)
        columns = self.get_table_columns('courses')
        expected_columns = [
            ('institution_id', 'TEXT'),
            ('institution_name', 'TEXT'),
            ('course_id', 'TEXT'),
            ('course_name', 'TEXT'),
            ('foe1_broad_field', 'TEXT'),
            ('foe1_narrow_field', 'TEXT'),
            ('foe1_detailed_field', 'TEXT'),
            ('course_level', 'TEXT'),
            ('course_duration', 'INTEGER'),
            ('tuition_fee', 'REAL'),
            ('non_tuition_fee', 'REAL'),
            ('total_course_cost', 'REAL')
        ]
        self.assertEqual(columns, expected_columns,
                         "Courses table schema is incorrect")

    # Test handling of an already existing table
    def test_table_already_exists(self):
        """Test the script's handling of existing tables"""
        create_institutions_table(self.con)  # First creation should work
        try:
            # Second attempt should not fail
            create_institutions_table(self.con)
            success = True
        except sqlite3.OperationalError:
            success = False
        self.assertTrue(
            success, "Table creation should handle existing tables without error.")

    # Normal test case for importing CSV
    @patch('pandas.read_csv')
    @patch('pandas.DataFrame.to_sql')
    def test_import_csv_to_sqlite(self, mock_to_sql, mock_read_csv):
        """Test normal import of CSV data"""
        # Mocking read_csv and to_sql
        mock_df = pd.DataFrame({
            'col1': ['value1', 'value2'],
            'col2': ['value3', 'value4']
        })
        mock_read_csv.return_value = mock_df

        # Run the import function
        import_csv_to_sqlite('dummy.csv', 'test_table', self.con)

        # Check if to_sql was called with correct parameters
        mock_to_sql.assert_called_once_with(
            'test_table', self.con, if_exists='append', index=False)


if __name__ == '__main__':
    unittest.main()
