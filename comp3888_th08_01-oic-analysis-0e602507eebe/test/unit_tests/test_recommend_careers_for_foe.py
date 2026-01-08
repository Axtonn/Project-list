import sqlite3
import unittest
from unittest.mock import patch
from application.career_rec.display_careers import (
    recommend_careers_for_foe, get_career_dataframes, summarize_salaries)


class test_recommend_careers_for_foe(unittest.TestCase):
    @classmethod
    def setUp(self):
        """Set up an in-memory SQLite database for testing"""
        con = sqlite3.connect(":memory:")
        con.execute("""
            CREATE TABLE careers (
                career_id INTEGER PRIMARY KEY,
                career_name TEXT)
            """)
        con.execute("""
            CREATE TABLE degree_requirements (
                requirement_id INTEGER PRIMARY KEY,
                foe_code TEXT,
                career_id INTEGER,
                matched_weight FLOAT,
                FOREIGN KEY(career_id) REFERENCES careers(career_id)
            )
            """)
        con.execute("""
            CREATE TABLE growth_data (
                occupation TEXT,
                "2028_job_growth" FLOAT,
                "2033_job_growth" FLOAT,
                national_shortage_raiting TEXT
            )
            """)

        con.execute("""
            CREATE TABLE salaries (
                careers_id INTEGER,
                satisfaction FLOAT, 
                review_num INTEGER,
                salary FLOAT,
                weak_link INTEGER
            )
        """)
        con.executemany("INSERT INTO careers(career_name) VALUES(?)", [
            ("career1",),
            ("career2",),
            ("career3",),
            ("career4",),
            ("career5",),
            ("career6",),
            ("career7",),
            ("career8",),
            ("career9",),
            ("career10",),
        ])
        con.executemany(
            """INSERT INTO degree_requirements(
                    foe_code, career_id, matched_weight
                ) VALUES(?, ?, ?)""",
            [
                ("foe1", 1, 0.05),
                ("foe1", 2, 0.4),
                ("foe1", 2, 0.4),
                ("foe1", 3, 0.5),
                ("foe1", 3, 0.3),
                ("foe1", 3, 0.1),
                ("foe1", 4, 0.07),
                ("foe1", 5, 0.1),
                ("foe1", 5, 0.1),
                ("foe1", 10, 0.1),
                ("foe2", 3, 0.1),
                ("foe2", 3, 0.1),
                ("foe2", 3, 0.1),
                ("foe2", 3, 0.1),
                ("foe2", 3, 0.1),
                ("foe2", 10, 0.85),
                ("foe2", 10, 0.85),
                ("foe3", 7, 0.1),
                ("foe4", 1, 1),
                ("foe4", 2, 1),
                ("foe4", 3, 1),
                ("foe4", 4, 1),
                ("foe4", 5, 1),
                ("foe4", 6, 1),
                ("foe4", 7, 1),
                ("foe4", 8, 1),
                ("foe4", 9, 1),
                ("foe4", 10, 1),
            ])
        con.executemany(
            """INSERT INTO growth_data(
                    occupation, "2028_job_growth", "2033_job_growth",
                    national_shortage_raiting
                ) VALUES(?, ?, ?, ?)""",
            [
                ("career1", -10, 10, "No Shortage"),
                ("career2", 10, -10, "No Shortage"),
                ("career3", 20, 20, "Shortage"),
                ("career4", 30, -20, "Regional Shortage"),
                ("career5", 50, 0, "Shortage"),
            ])
        con.executemany(
            """INSERT INTO salaries(
                    careers_id,
                    satisfaction,
                    review_num
                ) VALUES(?, ?, ?)""",
            [
                (1, 5, 16),
                (1, 4, 4),
            ])
        con.commit()
        self.con = con
        self.cursor = self.con.cursor()

    @classmethod
    def tearDown(self):
        """Close the database connection after each test"""
        self.con.close()

    def test_recommends_5_ordered_careers_for_foe(self):
        results = recommend_careers_for_foe(
            self.con, 'foe4', prioritise_uncommon=False)
        self.assertEqual(results, [
            ('career3', None, 20, 20, "Shortage", 1 * 1.5 * 1.5),
            ('career5', None, 50, 0, "Shortage", 1 * 1.1 * 1.5),
            ('career1', 4.8, -10, 10, "No Shortage", 1 * 1.3 * 1),
            ('career6', None, None, None, None, 1.0),
            ('career7', None, None, None, None, 1.0),
        ])

    def test_recommends_5_repeating(self):
        results = recommend_careers_for_foe(
            self.con, 'foe1', prioritise_uncommon=False)
        self.assertEqual(results, [
            ('career3', None, 20, 20, "Shortage", 0.9 * 1.5 * 1.5),     # 2.025
            ('career2', None, 10, -10, "No Shortage", 0.8 * 0.9 * 1),   # 0.72
            ("career5", None, 50, 0, "Shortage", 0.2 * 1.1 * 1.5),      # 0.33
            ("career10", None, None, None, None, 0.1),                  # 0.1
            ('career1', 4.8, -10, 10, "No Shortage", 0.05 * 1.3 * 1),   # 0.065
        ])

    def test_recommends_none_careers_for_invalid_foe(self):
        results = recommend_careers_for_foe(
            self.con, 'bad', prioritise_uncommon=False)
        self.assertEqual(results, [])

    def test_values_rarity_if_selected(self):
        self.maxDiff = None

        # Although career3 is usually greatly weighted, its priority drops
        # because it is too common
        results = recommend_careers_for_foe(
            self.con, 'foe1', prioritise_uncommon=True)
        self.assertEqual(results, [
            ('career2', None, 10, -10, "No Shortage", 0.8/3 * 0.9 * 1),   # 0.24
            ('career3', None, 20, 20, "Shortage", 0.9/9 * 1.5 * 1.5),     # 0.225
            ("career5", None, 50, 0, "Shortage", 0.2/3 * 1.1 * 1.5),      # 0.11
            ('career1', 4.8, -10, 10, "No Shortage", 0.05/2 * 1.3 * 1),  # 0.0325
            ('career4', None, 30, -20, "Regional Shortage",
                0.07/2 * 0.7 * 1.25),                               # 0.0306
        ])

    def test_recommends_less_than_5_if_none_available(self):
        # Although career3 is usually greatly weighted, its priority drops
        # because it is too common
        results = recommend_careers_for_foe(
            self.con, 'foe3', prioritise_uncommon=True)
        self.assertEqual(results, [('career7', None, None, None, None, 0.05)])

    @patch("application.career_rec.display_careers.recommend_careers_for_foe")
    def test_recommended_dataframes_formatted_correctly(self, mock_recommend_careers):
        mock_recommend_careers.side_effect = [[
            ('career1', None, None, None, 0.1)], [
            ('career2', None, None, None, 0.2)],]

        result = get_career_dataframes(
            [{"code": "foe1", "name": "FOE 1"},
             {"code": "foe1", "name": "FOE 1 again"},
             {"code": "foe2", "name": "FOE 2"},], False, False)

        self.assertEqual(mock_recommend_careers.call_count, 2)
        mock_recommend_career_calls = [
            mock_call.args[1:] for mock_call in mock_recommend_careers.call_args_list]
        self.assertEqual(mock_recommend_career_calls, [
            ('foe1', False, False),
            ('foe2', False, False),
        ])
        self.assertEqual(result, {
            "foe1": ("FOE 1",
                     ['N/A', 'N/A', 'N/A', 'N/A', 'N/A'],
                     [('career1', None, None, None, 0.1)]),
            "foe2": ("FOE 2",
                     ['N/A', 'N/A', 'N/A', 'N/A', 'N/A'],
                     [('career2', None, None, None, 0.2)]),
        })

    def test_summarizes_salaries_multiple(self):
        self.con.executemany(
            """INSERT INTO salaries(
                    careers_id,
                    salary,
                    weak_link
                ) VALUES(?, ?, ?)""",
            [
                (3, 70000, 0),
                (2, 60000, 0),
                (5, 100000, 0),
                (3, 0, 2),
            ])
        result = summarize_salaries(self.con, "foe1")
        self.assertEqual(
            list(result), [60000.0, 62500.0, 65000.0, 67500.0, 70000.0])

    def test_summarizes_salaries_none(self):
        self.con.execute("""DELETE FROM salaries""")
        result = summarize_salaries(self.con, "foe1")
        self.assertEqual(result, ["N/A", "N/A", "N/A", "N/A", "N/A"])
