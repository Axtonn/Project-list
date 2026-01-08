import sqlite3
import unittest
from unittest.mock import MagicMock, patch
from scripts.admissions.admission_center import AdmissionCenter
from scripts.admissions.atar_data_helper import (
    check_admission_requirements_exist,
    find_matching_course,
    insert_admission_requirement)


@patch('builtins.print')
@patch('scripts.common.db_writer.sqlite3.connect')
class TestAdmissionsDataFunctions(unittest.TestCase):

    def fill_course_admissions_table(self):
        self.con.execute("""
            CREATE TABLE courses (
                course_id TEXT PRIMARY KEY,
                institution_id TEXT,
                course_name TEXT
            )""")
        self.con.executemany("""
            INSERT INTO courses(
                course_id,
                institution_id,
                course_name) VALUES (?,?,?)
            """, [
            ("0123456A", "00001K", "Bachelor of Science"),
            ("0123456B", "00001K", "Bachelor of science"),
            ("0485819K", "22012A", "bachelor of Computing"),
            ("8834711L", "220001", "Master of Finance"),
            ("8834711J", "220001", "Bachelor of Arts")
        ])

        self.con.execute("""
            CREATE TABLE course_admission_requirements (
                course_id TEXT PRIMARY KEY,
                admission_org TEXT 
                    CHECK(admission_org IN 
                    ('UAC', 'VTAC', 'QTAC', 'SATAC', 'TISC', 'UTAS')),
                atar_guaranteed FLOAT,
                atar_min_non_adj FLOAT,
                atar_med_non_adj FLOAT,
                atar_min_adj FLOAT,
                atar_med_adj FLOAT,
                admission_org_code TEXT,
                FOREIGN KEY(course_id) REFERENCES courses(course_id)
            )
            """)

        self.con.executemany("""
            INSERT INTO course_admission_requirements(
                course_id,
                admission_org,
                admission_org_code) VALUES(?,?,?)
            """, [
            ("0123456A", "UAC", "1000123"),
            ("0123456B", "UAC", "P000123"),
            ("0485819K", "VTAC", None),
        ])

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

    def test_admission_internal_code_already_exist_true(self, mock_connect, _mock_print):
        mock_connect.return_value = self.con
        self.fill_course_admissions_table()
        self.assertTrue(check_admission_requirements_exist(
            AdmissionCenter.UAC, internal_code="1000123"))

    def test_admission_internal_code_does_not_exist_false(self, mock_connect, _mock_print):
        mock_connect.return_value = self.con
        self.fill_course_admissions_table()

        self.assertFalse(check_admission_requirements_exist(
            AdmissionCenter.VTAC, internal_code="1000123"))

    def test_admission_cricos_already_exist_true(self, mock_connect, _mock_print):
        mock_connect.return_value = self.con
        self.fill_course_admissions_table()
        self.assertTrue(check_admission_requirements_exist(
            AdmissionCenter.UAC, cricos_code="0123456B"))

    def test_admission_cricos_does_not_exist_false(self, mock_connect, _mock_print):
        mock_connect.return_value = self.con
        self.fill_course_admissions_table()
        self.assertFalse(check_admission_requirements_exist(
            AdmissionCenter.UAC, cricos_code="8834711L"))

    def test_admission_errors_does_not_exist(self, mock_connect, _mock_print):
        mock_cursor = MagicMock()
        mock_connect.return_value.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = sqlite3.OperationalError

        self.fill_course_admissions_table()
        self.assertFalse(check_admission_requirements_exist(
            AdmissionCenter.UAC, internal_code="1000123"))

    def test_admission_false_no_cricos_or_internal_code(self, mock_connect, _mock_print):
        mock_connect.return_value = self.con
        self.fill_course_admissions_table()
        self.assertFalse(check_admission_requirements_exist(
            AdmissionCenter.UAC))

    def test_finds_matching_course_case_insensitive(self, mock_connect, _mock_print):
        mock_connect.return_value = self.con
        self.fill_course_admissions_table()
        result = find_matching_course("00001K", "bachelor of science")
        self.assertEqual(result, ["0123456A", "0123456B"])

    def test_does_not_find_matching_course(self, mock_connect, _mock_print):
        mock_connect.return_value = self.con
        self.fill_course_admissions_table()
        result = find_matching_course("00001K", "bachelor of arts")
        self.assertEqual(result, [])

    def test_does_not_find_matching_course_on_error(self, mock_connect, _mock_print):
        mock_cursor = MagicMock()
        mock_connect.return_value.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = sqlite3.OperationalError
        self.fill_course_admissions_table()
        result = find_matching_course("00001K", "bachelor of arts")
        self.assertEqual(result, [])

    def test_inserts_single_admissions_row(self, mock_connect, _mock_print):
        mock_connect.return_value = self.con
        self.fill_course_admissions_table()
        result = insert_admission_requirement(
            course_id="8834711J",
            admission_center=AdmissionCenter.SATAC,
            center_code="123456", guaranteed=93.50,
            atars=[85, 92, 87, 95])
        self.assertTrue(result)
        entry = self.con.execute("""
                         SELECT * FROM course_admission_requirements 
                         WHERE course_id='8834711J'""").fetchone()
        self.assertEqual(
            entry, ('8834711J', 'SATAC', 93.5, 85.0, 92.0, 87.0, 95.0, '123456'))

    def test_skips_if_exists(self, mock_connect, _mock_print):
        mock_connect.return_value = self.con
        self.fill_course_admissions_table()
        result = insert_admission_requirement(
            course_id="0123456A",
            admission_center=AdmissionCenter.SATAC,
            center_code="123456", guaranteed=93.50,
            atars=[85, 92, 87, 95])
        self.assertTrue(result)
        entry = self.con.execute("""
                         SELECT * FROM course_admission_requirements 
                         WHERE course_id='0123456A'""").fetchone()
        self.assertEqual(
            entry, ('0123456A', 'UAC', None, None, None, None, None, '1000123'))

    def test_does_insert_on_error(self, mock_connect, _mock_print):
        mock_cursor = MagicMock()
        mock_connect.return_value.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = sqlite3.OperationalError
        self.fill_course_admissions_table()
        self.assertFalse(insert_admission_requirement(
            course_id="0123456A",
            admission_center=AdmissionCenter.SATAC,
            center_code="123456", guaranteed=93.50,
            atars=[85, 92, 87, 95]))


if __name__ == '__main__':
    unittest.main()
