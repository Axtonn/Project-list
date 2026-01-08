import sqlite3
import unittest
from unittest.mock import patch, MagicMock

from application.functionalities import generate_combined_output
from scripts.common.db_writer import DbWriter


class test_generate_combined_output(unittest.TestCase):
    @patch("builtins.open")
    @patch("application.functionalities.json")
    @patch("application.functionalities.get_career_dataframes")
    @patch("application.functionalities.get_degree_dataframes")
    def test_writes_to_temp_file(self, _mock_get_degrees, _mock_get_careers, mock_json, mock_open):
        generate_combined_output([], [], [], 700, {}, None, False, 0)
        mock_fp = MagicMock()
        mock_open.return_value = mock_fp
        mock_open.assert_called_once()
        mock_json.dump.assert_called_once()

    @patch("builtins.open")
    @patch("application.functionalities.json")
    @patch("application.functionalities.get_career_dataframes")
    @patch("application.functionalities.get_degree_dataframes")
    def test_default_call(self, mock_get_degrees, mock_get_careers, _mock_json, _mock_open):
        result = generate_combined_output(
            None, None, None, None, None, None, False, 0)
        mock_get_degrees.assert_called_once_with([], None, None, None)
        mock_get_careers.assert_called_once_with([], False, 0)
        self.assertEqual(result[0], {"recommendations": []})

    @patch("builtins.open")
    @patch("application.functionalities.json")
    @patch("application.functionalities.get_career_dataframes")
    @patch("application.functionalities.get_degree_dataframes")
    def test_fills_name(self, mock_get_degrees, mock_get_careers, _mock_json, _mock_open):
        target_courses = [
            ["USyd", "Bachelor of Science", 48, 120000,
             None, None, 83, "UAC", "123091"],
            ["UNSW", "Bachelor of Arts", 48, 115000,
             74.22, 85.55, None, "UAC", "909777"],
        ]
        mock_get_degrees.return_value = {
            "foe1": ("Field of Education 1", {"target": target_courses, "reach": [], "other": []}),
            "foe2": ("Field of Education 2", {"target": [], "reach": [[]], "other": []})
        }
        mock_get_careers.return_value = {
            "foe1": ("Field of Education 1",
                     [60000, 70000, 80000, 90000, 100000],
                     [["career1", None, 1, 2, None, 0.3],
                      ["career2", 3.8, 4, 5, "Shortage", 0.6]])}

        result = generate_combined_output(
            None, None, None, None, None, None, False, 0)
        expected_result = {"recommendations": [
            {"foe_code": "foe1",
             "name": "Field of Education 1",
             "salary_summary": {
                 "minimum": 60000,
                 "q1": 70000,
                 "median": 80000,
                 "q3": 90000,
                 "maximum": 100000
             },
             "courses": {
                 "target": [{"course_university": "USyd",
                             "course_name":  "Bachelor of Science",
                             "course_length": 48,
                             "course_total_cost": 120000,
                             "atar_min_non_adj": None,
                             "atar_med_non_adj":  None,
                             "atar_guaranteed":  83,
                             "admission_center": "UAC",
                             "admission_center_code": "123091"},
                            {"course_university": "UNSW",
                             "course_name": "Bachelor of Arts",
                             "course_length": 48,
                             "course_total_cost": 115000,
                             "atar_min_non_adj": 74.22,
                             "atar_med_non_adj":  85.55,
                             "atar_guaranteed":  None,
                             "admission_center": "UAC",
                             "admission_center_code": "909777"}],
                 "reach": [],
                 "other": []
             },
             "careers": [{"career_name": "career1",
                          "career_growth_2028": 1,
                          "career_growth_2033": 2,
                          "future_skill_shortage": None,
                          "satisfaction": None, },
                         {"career_name": "career2",
                          "career_growth_2028": 4,
                          "career_growth_2033": 5,
                          "future_skill_shortage": "Shortage",
                          "satisfaction": 3.8}]},
            {"foe_code": "foe2",
             "name": "Field of Education 2",
             "courses": {
                 "target": [],
                 "reach": [],
                 "other": []
             },
             "careers": []}
        ]}

        self.maxDiff = None
        self.assertEqual(result[0], expected_result)


if __name__ == '__main__':
    unittest.main()
