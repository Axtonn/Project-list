from pathlib import Path
import unittest
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.remote.webelement import WebElement
from scripts.common.element_matcher import find_text, extract_degree_requirements, last_index


@unittest.skip('Skipping the unit tests due to pipeline environment')
class TestElementMatcher(unittest.TestCase):
    driver = None

    @classmethod
    def setUpClass(self):
        options = ChromeOptions()
        options.add_argument("--headless=new")
        self.driver = Chrome(options)
        self.test_data_url = "file://" + \
            str(Path(__file__).parent) + \
            "/test_data/mock_job_search.html"
        self.driver.get(self.test_data_url)

    @classmethod
    def tearDownClass(self):
        if self.driver:
            self.driver.close()

    def test_find_text_in_top_level_tag(self):
        found_element = find_text(self.driver, "div", "Top level div")
        self.assertIsInstance(found_element, WebElement)
        self.assertEqual(found_element.text, "Top level div")

    def test_find_text_in_nested_tag(self):
        found_element = find_text(self.driver, "li", "Job metadata item 1")
        self.assertIsInstance(found_element, WebElement)
        self.assertEqual(found_element.text, "Job metadata item 1")

    def test_find_text_returns_with_partial_match(self):
        found_element = find_text(self.driver, "div", "Top level")
        self.assertIsInstance(found_element, WebElement)
        self.assertEqual(found_element.text, "Top level div")

    def test_find_text_returns_first_match(self):
        found_element = find_text(self.driver, "li", "Job metadata")
        self.assertIsInstance(found_element, WebElement)
        self.assertIn("Job metadata item 1", found_element.text)

    def test_find_text_returns_partial_with_other_children(self):
        # Edge case: As long as the text exists in the tag, it should not
        # matter if the tag contains nested children.
        found_element = find_text(self.driver, "div", "Another")
        self.assertIsInstance(found_element, WebElement)
        self.assertIn("Another top", found_element.text)

    def test_does_not_find_partial_match_in_children(self):
        # Negative case: if an element has a child tag with the relevant data,
        # it should not be returned
        found_element = find_text(self.driver, "div", "Job details")
        self.assertIsNone(found_element)

    def test_extract_degree_requirements_matches_bachelors(self):
        text = "<li>Random starting string Bachelor's of Engineering</li>"
        matches = extract_degree_requirements(text)
        self.assertEqual(len(matches), 1)
        self.assertIn("Bachelor's of Engineering", matches)

    def test_extract_degree_requirements_matches_masters(self):
        text = "<li>this is a long string before the actual text master's " + \
            "in engineering with additonal details</li>"
        matches = extract_degree_requirements(text)
        self.assertEqual(len(matches), 1)
        self.assertIn(
            "master's in engineering with additonal details", matches)

    def test_extract_degree_requirements_multiple_degrees(self):
        text = "<a>phd in quantum physics</a><a>not important</a>" + \
            "<a>practicing md in science</a>"
        matches = extract_degree_requirements(text)
        self.assertEqual(len(matches), 2)
        self.assertIn("phd in quantum physics", matches)
        self.assertIn("md in science", matches)

    def test_extract_degree_requirements_multiple_degrees(self):
        text = "<a>phd in quantum physics</a><a>practicing md in science</a>"
        matches = extract_degree_requirements(text)
        self.assertEqual(len(matches), 2)
        self.assertIn("phd in quantum physics", matches)
        self.assertIn("md in science", matches)

    def test_extract_degree_requirements_degree(self):
        text = "<>a bachelor's degree in economics</>"
        matches = extract_degree_requirements(text)
        self.assertEqual(len(matches), 1)
        self.assertIn("a bachelor's degree in economics", matches)

    def test_extract_degree_requirements_no_degree_of(self):
        text = "<>high degree of skill</>"
        matches = extract_degree_requirements(text)
        self.assertEqual(len(matches), 0)

    def test_last_index_finds_last(self):
        # Positive case
        ls = [1, 2, 3, 3, 5]
        i = last_index(ls, 3)
        self.assertEqual(i, 3)

    def test_last_index_finds_first_if_uniq(self):
        ls = [1, 2, 3, 3, 5]
        i = last_index(ls, 2)
        self.assertEqual(i, 1)

    def test_last_index_raises_error_if_not_exists(self):
        ls = [1, 2, 3, 3, 5]
        with self.assertRaises(ValueError):
            last_index(ls, 0)


if __name__ == '__main__':
    unittest.main()
