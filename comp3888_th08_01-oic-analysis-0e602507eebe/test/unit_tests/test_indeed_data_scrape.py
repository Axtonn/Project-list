import unittest
from unittest.mock import patch, Mock, call, MagicMock
from scripts.job_degree_scrapers.indeed_data_scrape import run_scraper, extract_job_details
from selenium.webdriver.common.by import By


@patch("scripts.job_degree_scrapers.indeed_data_scrape.time")
@patch("scripts.job_degree_scrapers.indeed_data_scrape.DbWriter")
@patch('builtins.print')
class test_indeed_data_scrape(unittest.TestCase):
    popup_call = call(By.CLASS_NAME, "DesktopJobAlertPopup-heading")
    find_jobs_call = call('class name', 'jcs-JobTitle')
    find_next_page_call = call(
        'xpath', "//a[contains(@aria-label, 'Next Page')]")
    find_job_description_call = call(By.ID, "jobDescriptionText")
    find_location_call = call(
        By.XPATH, "//div[contains(@data-testid, 'companyLocation')]/div")
    find_pay_call = call(
        By.XPATH, "//h3[text()='Pay']/following-sibling::div//div[contains(text(), '$')]")

    def test_no_jobs_no_pages_found_exits(
            self, _mock_print, _mock_dbwriter, _mock_time):
        mock_chrome = Mock()
        mock_chrome.find_elements = Mock(return_value=[])
        run_scraper(mock_chrome)
        # Looked for popups, jobs, and then next page
        mock_chrome.find_elements.assert_has_calls(
            [self.popup_call,
             self.find_jobs_call,
             self.find_next_page_call])
        mock_chrome.close.assert_called_once()

    def test_accesses_job_details(
            self, _mock_print, mock_dbwriter, _mock_time):
        mock_chrome = Mock()
        mock_job = MagicMock()
        mock_execute = mock_dbwriter.return_value.execute

        mock_chrome.find_elements = Mock(
            side_effect=[[], [mock_job, mock_job], [], [], [], [], []])
        run_scraper(mock_chrome)

        self.assertEqual(mock_job.click.call_count, 2)
        mock_chrome.find_elements.assert_has_calls(
            [self.popup_call,
             self.find_jobs_call,
             self.popup_call,  # Checks for popups in first job
             self.find_job_description_call,  # Extract first job data
             self.popup_call,  # Checks for popups in second job
             self.find_job_description_call,  # Extract second job data
             self.find_next_page_call])
        mock_chrome.close.assert_called_once()
        mock_execute.assert_not_called()

    def test_writes_non_empty_requirements(
            self, _mock_print, mock_dbwriter, _mock_time):
        mock_chrome = Mock()
        mock_job = MagicMock()
        mock_job_detail = Mock()

        mock_job_detail.get_attribute = Mock(
            return_value="<li>master of space</li>")
        mock_chrome.find_elements = Mock(
            side_effect=[[], [mock_job], [], [mock_job_detail], [], [], []])

        mock_execute = mock_dbwriter.return_value.execute

        run_scraper(mock_chrome)

        mock_job.click.assert_called_once()
        mock_chrome.find_elements.assert_has_calls(
            [self.popup_call,
             self.find_jobs_call,
             self.popup_call,  # Checks for popups in first job
             self.find_job_description_call,  # Extract first job data
             self.find_location_call,
             self.find_pay_call,
             self.find_next_page_call])
        self.assertEqual(mock_execute.call_count, 2)
        mock_chrome.close.assert_called_once()

    def test_extracts_empty_list(
            self, _mock_print, _mock_dbwriter, _mock_time):
        mock_chrome = Mock()
        mock_chrome.find_elements = Mock(side_effect=[[]])

        result = extract_job_details(mock_chrome)
        self.assertEqual(result, ([], None, None))

    def test_extracts_empty_if_no_requirements(
            self, _mock_print, _mock_dbwriter, _mock_time):
        mock_chrome = Mock()
        mock_job_detail = Mock()
        mock_location = Mock()
        mock_location.text = "NSW"

        mock_pay = Mock()
        mock_pay.text = "$100 per week"

        mock_job_detail.get_attribute = Mock(
            return_value="nothing")

        mock_chrome.find_elements = Mock(
            side_effect=[[mock_job_detail], [mock_location], [mock_pay]])

        result = extract_job_details(mock_chrome)
        self.assertEqual(result, ([], None, None))

    def test_extracts_none_if_location_pay_empty(
            self, _mock_print, _mock_dbwriter, _mock_time):
        mock_chrome = Mock()
        mock_job_detail = Mock()

        mock_job_detail.get_attribute = Mock(
            return_value="<li>master of space</li>")

        mock_chrome.find_elements = Mock(
            side_effect=[[mock_job_detail], [], []])

        result = extract_job_details(mock_chrome)
        self.assertEqual(result, (["master of space"], None, None))

    def test_extracts_exists_if_location_pay_non_empty(
            self, _mock_print, _mock_dbwriter, _mock_time):
        mock_chrome = Mock()
        mock_job_detail = Mock()

        mock_location = Mock()
        mock_location.text = "NSW"

        mock_pay = Mock()
        mock_pay.text = "$100 per week"

        mock_job_detail.get_attribute = Mock(
            return_value="<li>master of space</li>")

        mock_chrome.find_elements = Mock(
            side_effect=[[mock_job_detail], [mock_location], [mock_pay]])

        result = extract_job_details(mock_chrome)
        self.assertEqual(result, (["master of space"], "NSW", "$100 per week"))


if __name__ == '__main__':
    unittest.main()
