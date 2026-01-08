import os
import unittest
from selenium.common.exceptions import NoSuchElementException
from unittest.mock import patch, MagicMock, call

from scripts.admissions.admission_center import AdmissionCenter
from scripts.admissions.uac.uac_parser import (
    get_data_from_tab, handle_atar_table, input_institution_name, write_data)


@patch('builtins.print')
class TestUACParser(unittest.TestCase):
    mock_atar_path = os.getcwd() \
        + "/test/unit_tests/test_data/mock_atar.html"
    mock_multiple_atar_path = os.getcwd() \
        + "/test/unit_tests/test_data/mock_atar_multiple.html"

    def test_inputs_correct_name(self, _mock_print):
        mock_driver = MagicMock()
        mock_search_div = MagicMock()
        mock_search_element = MagicMock()
        mock_driver.find_element.return_value = mock_search_div
        mock_search_div.find_element.return_value = mock_search_element

        self.assertTrue(input_institution_name(mock_driver, "USyd"))
        self.assertEqual(mock_driver.find_element.call_count, 1)
        self.assertEqual(mock_search_div.find_element.call_count, 1)
        mock_search_element.send_keys.assert_called_once_with("USyd")

    def test_input_fails_on_element_not_found(self, _mock_print):
        mock_driver = MagicMock()
        mock_search_div = MagicMock()
        mock_driver.find_element.return_value = mock_search_div
        mock_search_div.find_element.side_effect = NoSuchElementException

        self.assertFalse(input_institution_name(mock_driver, "USyd"))
        self.assertEqual(mock_driver.find_element.call_count, 1)
        self.assertEqual(mock_search_div.find_element.call_count, 1)

    def test_handle_atar_table(self, _mock_print):
        with open(self.mock_atar_path) as atar_html:
            result = handle_atar_table(atar_html)
        self.assertEqual(result, [90.4, 95.35, 91.23, 96.0])

    def test_handle_atar_table_mult_rows(self, _mock_print):
        with open(self.mock_multiple_atar_path) as atar_html:
            result = handle_atar_table(atar_html)
        self.assertEqual(result, [87, 94, 89, 97])

    @patch("scripts.admissions.uac.uac_parser.BeautifulSoup")
    def test_handle_atar_table_no_data_in_any(self, mock_soup, _mock_print):
        mock_table = MagicMock()
        mock_element = MagicMock()
        mock_element.get_text.side_effect = [
            "99", "98", "97", "NN"]
        mock_table.return_value = [mock_element] * 6
        mock_soup.return_value.find_all = mock_table
        result = handle_atar_table("")
        self.assertEqual(result, [])

        mock_element.get_text.side_effect = [
            "99", "-", "98", "97", ]
        result = handle_atar_table("")
        self.assertEqual(result, [])

        mock_element.get_text.side_effect = [
            "99", "NP", "98", "97"]
        result = handle_atar_table("")
        self.assertEqual(result, [])

        mock_element.get_text.side_effect = [
            "99", "-10", "98", "97"]
        result = handle_atar_table("")
        self.assertEqual(result, [])

        mock_element.get_text.side_effect = [
            "99", "100", "98", "97"]
        result = handle_atar_table("")
        self.assertEqual(result, [])

        mock_element.get_text.side_effect = [
            "99", "not a value", "98", "97"]
        result = handle_atar_table("")
        self.assertEqual(result, [])

    @patch("scripts.admissions.uac.uac_parser.BeautifulSoup")
    def test_handle_atar_table_no_data_keep_no_data(self, mock_soup, _mock_print):
        mock_table = MagicMock()
        mock_element = MagicMock()
        mock_element.get_text.side_effect = ["<5", "N/A", "NC", "NO"]
        mock_table.return_value = [mock_element] * 6
        mock_soup.return_value.find_all = mock_table
        result = handle_atar_table("")
        self.assertEqual(result, [None, None, None, None])

        mock_element.get_text.side_effect = ["NR", "NS", "98", "99"]
        result = handle_atar_table("")
        self.assertEqual(result, [None, None, 98, 99])

    @patch("scripts.admissions.uac.uac_parser.handle_atar_table")
    @patch("scripts.admissions.uac.uac_parser.WebDriverWait")
    def test_get_data_from_tab_all_data(self, mock_wait, mock_handle_atar_table, _mock_print):
        mock_driver = MagicMock()

        mock_cricos_num = MagicMock()
        mock_cricos_num.text = "CRICOS ID: 00123D dd"

        mock_course_name = MagicMock()
        mock_course_name.text = "Bachelor of computing"

        mock_internal_code = MagicMock()
        mock_internal_code.text = "11101"

        mock_handle_atar_table.return_value = [71, 72, 73, 74]

        mock_guaranteed_atar = MagicMock()
        mock_guaranteed_atar.text = "Guaranteed ATAR: 91.55"

        mock_driver.find_element.side_effect = [
            mock_cricos_num, mock_course_name, mock_internal_code, MagicMock()]
        mock_driver.find_elements.return_value = [mock_guaranteed_atar]

        result = get_data_from_tab(mock_driver)
        mock_wait.assert_called_once()
        self.assertEqual(
            result, (True, {'code': '11101',
                            'atars': [71, 72, 73, 74],
                            'course_name': 'Bachelor of computing',
                            'guaranteed_atar': 91.55,
                            'provider': '00123D'}))

    @patch("scripts.admissions.uac.uac_parser.WebDriverWait")
    def test_get_data_from_tab_no_cricos(self, mock_wait, _mock_print):
        mock_driver = MagicMock()
        mock_driver.find_element.side_effect = NoSuchElementException

        result = get_data_from_tab(mock_driver)
        mock_wait.assert_called_once()
        self.assertEqual(result, (False, {}))

    @patch("scripts.admissions.uac.uac_parser.WebDriverWait")
    def test_get_data_from_tab_no_course_name(self, mock_wait, _mock_print):
        mock_driver = MagicMock()

        mock_cricos_num = MagicMock()
        mock_cricos_num.text = "CRICOS ID: 00123D dd"

        mock_driver.find_element.side_effect = [
            mock_cricos_num, NoSuchElementException]

        result = get_data_from_tab(mock_driver)
        mock_wait.assert_called_once()
        self.assertEqual(result, (False, {}))

    @patch("scripts.admissions.uac.uac_parser.handle_atar_table")
    @patch("scripts.admissions.uac.uac_parser.WebDriverWait")
    def test_get_data_from_tab_missing_vals(self, mock_wait, mock_handle_atar_table, _mock_print):
        mock_driver = MagicMock()

        mock_cricos_num = MagicMock()
        mock_cricos_num.text = "CRICOS ID: 00123D dd"

        mock_course_name = MagicMock()
        mock_course_name.text = "Bachelor of computing"

        mock_handle_atar_table.return_value = [71, 72, 73, 74]

        mock_guaranteed_atar = MagicMock()
        mock_guaranteed_atar.text = "Guaranteed ATAR: 91.55"

        mock_driver.find_element.side_effect = [
            mock_cricos_num, mock_course_name, NoSuchElementException, MagicMock()]
        mock_driver.find_elements.side_effect = [[], []]

        result = get_data_from_tab(mock_driver)
        mock_wait.assert_called_once()
        self.assertEqual(
            result, (True, {'code': None,
                            'atars': [71, 72, 73, 74],
                            'course_name': 'Bachelor of computing',
                            'guaranteed_atar': None,
                            'provider': '00123D'}))

    @patch("scripts.admissions.uac.uac_parser.handle_atar_table")
    @patch("scripts.admissions.uac.uac_parser.WebDriverWait")
    def test_get_data_from_tab_missing_atars(self, mock_wait, mock_handle_atar_table, _mock_print):
        mock_driver = MagicMock()

        mock_cricos_num = MagicMock()
        mock_cricos_num.text = "CRICOS ID: 00123D dd"

        mock_course_name = MagicMock()
        mock_course_name.text = "Bachelor of computing"

        mock_handle_atar_table.return_value = []

        mock_driver.find_element.side_effect = [
            mock_cricos_num, mock_course_name, NoSuchElementException, MagicMock()]

        result = get_data_from_tab(mock_driver)
        mock_wait.assert_called_once()
        self.assertEqual(result, (False, {}))

    @patch("scripts.admissions.uac.uac_parser.handle_atar_table")
    @patch("scripts.admissions.uac.uac_parser.WebDriverWait")
    def test_get_data_from_tab_missing_atars(self, mock_wait, mock_handle_atar_table, _mock_print):
        mock_driver = MagicMock()

        mock_cricos_num = MagicMock()
        mock_cricos_num.text = "CRICOS ID: 00123D dd"

        mock_course_name = MagicMock()
        mock_course_name.text = "Bachelor of computing"

        mock_handle_atar_table.return_value = []

        mock_driver.find_element.side_effect = [
            mock_cricos_num, mock_course_name, NoSuchElementException, NoSuchElementException]

        result = get_data_from_tab(mock_driver)
        mock_wait.assert_called_once()
        self.assertEqual(result, (False, {}))

    @patch("scripts.admissions.uac.uac_parser.handle_atar_table")
    @patch("scripts.admissions.uac.uac_parser.WebDriverWait")
    def test_get_data_from_tab_cant_find_atars(self, mock_wait, mock_handle_atar_table, _mock_print):
        mock_driver = MagicMock()

        mock_cricos_num = MagicMock()
        mock_cricos_num.text = "CRICOS ID: 00123D dd"

        mock_course_name = MagicMock()
        mock_course_name.text = "Bachelor of computing"

        mock_handle_atar_table.return_value = []

        mock_driver.find_element.side_effect = [
            mock_cricos_num, mock_course_name, NoSuchElementException, MagicMock()]

        result = get_data_from_tab(mock_driver)
        mock_wait.assert_called_once()
        self.assertEqual(
            result, (False, {}))

    @patch("scripts.admissions.uac.uac_parser.insert_admission_requirement")
    @patch("scripts.admissions.uac.uac_parser.find_matching_course")
    @patch("scripts.admissions.uac.uac_parser.check_admission_requirements_exist")
    def test_write_data_succeeds_if_exists(self, mock_check_exist, mock_find_courses, mock_insert, _mock_print):
        mock_check_exist.return_value = True

        self.assertTrue(write_data({'code': None,
                                    'atars': [71, 72, 73, 74],
                                    'course_name': 'Bachelor of computing',
                                    'guaranteed_atar': None,
                                    'provider': '00123D'}, ask_input=False))
        mock_check_exist.assert_called_once()
        mock_find_courses.assert_not_called()
        mock_insert.assert_not_called()

    @patch("scripts.admissions.uac.uac_parser.insert_admission_requirement")
    @patch("scripts.admissions.uac.uac_parser.find_matching_course")
    @patch("scripts.admissions.uac.uac_parser.check_admission_requirements_exist")
    def test_write_data_multiple_inserts(self, mock_check_exist, mock_find_courses, mock_insert: MagicMock, _mock_print):
        mock_check_exist.return_value = False
        mock_find_courses.return_value = ["a", "b", "c"]

        self.assertTrue(write_data({'code': None,
                                    'atars': [71, 72, 73, 74],
                                    'course_name': 'Bachelor of computing',
                                    'guaranteed_atar': 80,
                                    'provider': '00123D'}, ask_input=False))
        mock_check_exist.assert_called_once()
        mock_find_courses.assert_called_once()
        mock_insert.assert_has_calls(
            [call("a", AdmissionCenter.UAC, None, 80, [71, 72, 73, 74]),
             call("b", AdmissionCenter.UAC, None, 80, [71, 72, 73, 74]),
             call("c", AdmissionCenter.UAC, None, 80, [71, 72, 73, 74])], any_order=True)

    @patch("scripts.admissions.uac.uac_parser.find_matching_course")
    @patch("scripts.admissions.uac.uac_parser.check_admission_requirements_exist")
    def test_write_data_no_match_no_input(self, mock_check_exist, mock_find_courses, _mock_print):
        mock_check_exist.return_value = False
        mock_find_courses.return_value = []

        self.assertFalse(write_data({'code': None,
                                     'atars': [71, 72, 73, 74],
                                     'course_name': 'Bachelor of computing',
                                     'guaranteed_atar': 80,
                                     'provider': '00123D'}, ask_input=False))

    @patch("builtins.input")
    @patch("scripts.admissions.uac.uac_parser.insert_admission_requirement")
    @patch("scripts.admissions.uac.uac_parser.find_matching_course")
    @patch("scripts.admissions.uac.uac_parser.check_admission_requirements_exist")
    def test_write_data_no_match_with_input(self, mock_check_exist, mock_find_courses, mock_insert: MagicMock, mock_input, _mock_print):
        mock_check_exist.return_value = False
        mock_find_courses.return_value = []
        mock_input.return_value = " 123 ,456 "

        self.assertTrue(write_data({'code': None,
                                    'atars': [71, 72, 73, 74],
                                    'course_name': 'Bachelor of computing',
                                    'guaranteed_atar': 80,
                                    'provider': '00123D'}, ask_input=True))
        mock_check_exist.assert_called_once()
        mock_find_courses.assert_called_once()
        mock_input.assert_called_once()
        mock_insert.assert_has_calls(
            [call("123", AdmissionCenter.UAC, None, 80, [71, 72, 73, 74]),
             call("456", AdmissionCenter.UAC, None, 80, [71, 72, 73, 74])], any_order=True)

    @patch("builtins.input")
    @patch("scripts.admissions.uac.uac_parser.find_matching_course")
    @patch("scripts.admissions.uac.uac_parser.check_admission_requirements_exist")
    def test_write_data_no_match_with_empty_input(self, mock_check_exist, mock_find_courses, mock_input, _mock_print):
        mock_check_exist.return_value = False
        mock_find_courses.return_value = []
        mock_input.return_value = " \n\t"

        self.assertFalse(write_data({'code': None,
                                    'atars': [71, 72, 73, 74],
                                     'course_name': 'Bachelor of computing',
                                     'guaranteed_atar': 80,
                                     'provider': '00123D'}, ask_input=True))
        mock_check_exist.assert_called_once()
        mock_find_courses.assert_called_once()
        mock_input.assert_called_once()


if __name__ == '__main__':
    unittest.main()
