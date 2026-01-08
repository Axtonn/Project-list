import sqlite3
import unittest
from unittest.mock import patch, MagicMock, call

from application.display_degrees import (
    get_degrees, get_degree_dataframes)
from scripts.common.db_writer import DbWriter


class test_recommend_degrees_for_foe(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        """Set up an in-memory SQLite database for testing"""
        con = sqlite3.connect("file::memory:?cache=shared", uri=True)
        con.execute("""
            CREATE TABLE institutions (
                institution_id TEXT PRIMARY KEY,
                institution_name TEXT,
                ranking INTEGER)
            """)
        con.execute("""
            CREATE TABLE courses (
                course_id TEXT PRIMARY KEY,
                course_duration INTEGER,
                total_course_cost REAL,
                foe1_narrow_field TEXT,
                institution_id TEXT,
                course_name TEXT,
                course_level TEXT)
            """)
        con.execute("""
            CREATE TABLE course_admission_requirements (
                course_id TEXT PRIMARY KEY,
                atar_min_non_adj FLOAT,
                atar_med_non_adj FLOAT,
                atar_guaranteed FLOAT,
                admission_org TEXT,
                admission_org_code TEXT
            )
            """)

        con.executemany(
            """INSERT INTO institutions(
                    institution_id, institution_name, ranking)
                VALUES(?, ?, ?)""", [
                ("123A", "USYD", 2),
                ("F29", "UNSW", 1),
                ("930", "Monash", 4),
                ("1000", "University of Fake Place", None)
            ])
        con.executemany(
            """INSERT INTO courses(
                    course_id, course_duration, total_course_cost,
                    foe1_narrow_field, institution_id, course_name, course_level)
                VALUES(?, ?, ?, ?, ?, ?, ?)""",
            [
                ("12345A", 96, 125, "0919", "123A",
                 "Bachelor of Science", "Bachelor Degree"),
                ("12345B", 96, 200, "0919", "F29",
                 "Bachelor of Arts", "Bachelor Degree"),
                ("555632", 48, 400, "0919", "930",
                 "Bachelor of History", "Bachelor Degree"),
                ("123452", 128, 100, "0919", "930",
                 "Bachelor of English", "Bachelor Degree"),
            ])
        con.executemany(
            """INSERT INTO course_admission_requirements(
                    course_id, atar_min_non_adj, atar_med_non_adj,
                    atar_guaranteed, admission_org, admission_org_code)
                VALUES(?, ?, ?, ?, ?, ?)""",
            [
                ("12345A", 70, 74.5, 80, "UAC", "12039102"),
                ("12345B", 80, 95, 98, "UAC", "0234513"),
                ("123452", 75, 79, 85, "VTAC", "301923"),
            ])
        con.commit()
        self.con = con
        self.cursor = self.con.cursor()

    @classmethod
    def tearDownClass(self):
        """Close the database connection after each test"""
        self.con.close()

    @patch.object(DbWriter, "DB_PATH", "file::memory:?cache=shared")
    def test_gets_degrees_grades_in_range(self):
        results = get_degrees("0919", grade=80, min_grade=75)
        expected = [['USYD', 'Bachelor of Science', 96, 125.0, 70.0, 74.5,
                     80.0, 'UAC', '12039102'],
                    ['Monash', 'Bachelor of English', 128, 100.0, 75.0,
                     79.0, 85.0, 'VTAC', '301923']]
        self.assertEqual(results, expected)

    @patch.object(DbWriter, "DB_PATH", "file::memory:?cache=shared")
    def test_gets_degrees_grades_in_range_high_min(self):
        results = get_degrees("0919", grade=83, min_grade=79)
        expected = [['USYD', 'Bachelor of Science', 96, 125.0, 70.0, 74.5,
                     80.0, 'UAC', '12039102']]
        self.assertEqual(results, expected)

    @patch.object(DbWriter, "DB_PATH", "file::memory:?cache=shared")
    def test_gets_degrees_default_matches_all(self):
        results = get_degrees("0919")
        expected = [
            ['UNSW', 'Bachelor of Arts', 96, 200.0,
                80.0, 95.0, 98.0, 'UAC', '0234513'],
            ['USYD', 'Bachelor of Science', 96, 125.0, 70.0, 74.5,
                80.0, 'UAC', '12039102'],
            ['Monash', 'Bachelor of History', 48,
             400.0, None, None, None, None, None],
            ['Monash', 'Bachelor of English', 128, 100.0, 75.0,
             79.0, 85.0, 'VTAC', '301923']
        ]
        self.assertEqual(results, expected)

    @patch("application.display_degrees.get_degrees")
    def test_no_foes_dataframes(self, _mock_get_degrees):
        self.assertEqual(get_degree_dataframes([], 100, None, None), {})

    @patch("application.display_degrees.get_degrees")
    def test_no_grade_given(self, mock_get_degrees):
        mock_get_degrees.return_value = [["fake"]]
        mock_foes = [{"code": "foe1", "name": "FOE Name"}]
        result = get_degree_dataframes(
            mock_foes, 100, None, None)
        mock_get_degrees.assert_called_once_with("foe1", 100000, None, None)
        self.assertEqual(
            result, {"foe1": ("FOE Name", {"target": [["fake"]], "reach": []})})

    @patch("application.display_degrees.get_degrees")
    def test_no_reach_degrees(self, mock_get_degrees: MagicMock):
        mock_get_degrees.side_effect = [
            [["deg1"]], [["deg2"]], [["deg3"]], [["deg4"], ["deg5"]]]
        mock_foes = [{"code": "foe1", "name": "FOE 1"},
                     {"code": "foe2", "name": "FOE 2"}]
        result = get_degree_dataframes(
            mock_foes, 100, None, 80)
        mock_get_degrees.assert_has_calls(
            [call('foe1', 100000, None, 81),
             call("foe1", 100000, None, 89.49166131012232, 81),
             call('foe2', 100000, None, 81),
             call("foe2", 100000, None, 89.49166131012232, 81),]
        )
        self.assertEqual(
            result, {"foe1": ("FOE 1",
                              {"target": [["deg1"]], "reach": [["deg2"]]}),
                     "foe2": ("FOE 2",
                              {"target": [["deg3"]], "reach": [["deg4"], ["deg5"]]})})


if __name__ == '__main__':
    unittest.main()
