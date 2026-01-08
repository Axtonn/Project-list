import unittest
from unittest.mock import patch, MagicMock
import sqlite3
import pandas as pd
import scripts.foe_script.foe_script as fs


@patch('builtins.print')
class TestFoeScript(unittest.TestCase):

    @patch('scripts.foe_script.foe_script.pd.read_excel')
    # @patch('builtins.print')
    def test_read_excel_file(self, mock_read_excel, mock_print):
        # Mock the panda.DataFrame returned by panda.read_excel
        mock_data_frame = pd.DataFrame({
            'Narrow Fields': ['0101', '0102'],
            'Unnamed: 2': ['Mathematics', 'Physics']
        })
        mock_read_excel.return_value = mock_data_frame

        # Call the function to read the Excel file
        data_frame = fs.read_excel_file('dummy_path.xlsx')

        # Check if the DataFrame is as expected
        self.assertEqual(data_frame.shape, (2, 2))
        self.assertEqual(list(data_frame.columns), [
                         'Narrow Fields', 'Unnamed: 2'])
        mock_print.assert_called_once_with(
            "Read Excel file from dummy_path.xlsx")

    def test_extract_narrow_fields(self, mock_print):
        # Create a mock DataFrame
        mock_data_frame = pd.DataFrame({
            'Narrow Fields': ['0101', '0102', None],
            'Unnamed: 2': ['Mathematics', 'Physics', None]
        })

        # Call the function to extract narrow fields
        narrow_fields = fs.extract_narrow_fields(mock_data_frame)

        # Check if the DataFrame is as expected
        self.assertEqual(narrow_fields.shape, (2, 2))
        self.assertEqual(list(narrow_fields.columns), ['code', 'name'])
        self.assertEqual(narrow_fields.iloc[0]['code'], '0101')
        self.assertEqual(narrow_fields.iloc[0]['name'], 'Mathematics')

    @patch('scripts.foe_script.foe_script.pd.DataFrame.to_csv')
    # @patch('builtins.print')
    def test_output_to_csv(self, mock_to_csv, mock_print):
        # Create a mock DataFrame
        mock_data_frame = pd.DataFrame({
            'code': ['0101', '0102'],
            'name': ['Mathematics', 'Physics']
        })

        # Call the function to write the DataFrame to CSV
        fs.output_to_csv(mock_data_frame, 'dummy_path.csv')

        # Check if the DataFrame was written to CSV
        mock_to_csv.assert_called_once_with('dummy_path.csv', index=False)
        # Check if the print statement was called
        mock_print.assert_called_once_with("Data saved to dummy_path.csv")

    @patch('scripts.foe_script.foe_script.sqlite3.connect')
    # @patch('builtins.print')  # Mock the print function
    def test_create_foe_table(self, mock_connect, mock_print):
        # Mock the SQLite connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # Call the function to create the 'foe' table
        fs.create_foe_table(mock_cursor)

        # Check if the correct SQL command was executed
        mock_cursor.execute.assert_called_once_with("""
            CREATE TABLE foe (
                code TEXT PRIMARY KEY,
                name TEXT
            )
        """)
        # Check if the print statement was called
        mock_print.assert_called_once_with("'foe' table created")

        # Simulate OperationalError
        mock_cursor.execute.side_effect = sqlite3.OperationalError
        fs.create_foe_table(mock_cursor)
        self.assertEqual(mock_cursor.execute.call_count, 2)
        # Check if the print statement was called again
        mock_print.assert_called_with("'foe' table already exists")

    @patch('scripts.foe_script.foe_script.sqlite3.connect')
    # @patch('builtins.print')
    def test_insert_into_database(self, mock_connect, mock_print):
        # Create a mock DataFrame
        mock_data_frame = pd.DataFrame({
            'code': ['0101', '0102'],
            'name': ['Mathematics', 'Physics']
        })

        # Mock the SQLite connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # Call the function to insert data into the database
        fs.insert_into_database(mock_data_frame, mock_cursor)

        # Check if the correct SQL commands were executed
        mock_cursor.execute.assert_any_call(
            "INSERT INTO foe (code, name) VALUES (?, ?)", ('0101', 'Mathematics'))
        mock_cursor.execute.assert_any_call(
            "INSERT INTO foe (code, name) VALUES (?, ?)", ('0102', 'Physics'))
        mock_print.assert_called_once_with(
            "Data successfully inserted into the database")

        # Simulate IntegrityError
        mock_cursor.execute.side_effect = sqlite3.IntegrityError
        fs.insert_into_database(mock_data_frame, mock_cursor)
        self.assertEqual(mock_cursor.execute.call_count, 3)
        mock_print.assert_called_with("Data already exists in the database")


if __name__ == '__main__':
    unittest.main()
