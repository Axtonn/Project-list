"""
    Helper functions for locating matches within text and lists
"""
import re
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException


def find_text(driver: 'WebDriver', tag_type: str, text_match: str):
    """
    Function: find_text
    ----------------------------
        Returns a WebElement matching the given tag and text. Searches the DOM from the root.

        tag_type: the tag of the requested element (e.g. li for <li></li>)
        text_match: the text value in the immediate body of the requested element

        returns: the matching element or None, if it does not exist.
    """
    matcher = f"//{tag_type}[contains(text(), '{text_match}')]"

    try:
        return driver.find_element(By.XPATH, matcher)
    except NoSuchElementException:
        return None


def extract_degree_requirements(base_text: str):
    """
    Function: extract_degree_requirements
    ----------------------------
        Finds and returns a list of all strings in the form of "bachelor of ...",
        "bachelor in ...", and variations using masters, phd, and md to replace "bachelor"

        base_text: base text from which to locate degree details

        returns: a list of all matches
    """
    degree_matcher = r'(?:(?:bachelor|master|phd |md ).{0,4}(?:in|of)|(?<=>).{0,20}degree(?: in)).*?(?=[\.\n<])'
    return re.findall(degree_matcher, base_text, flags=re.I)


def last_index(ls: list, element: any):
    """
    Locates the last index of an element occurring in a list.

    Args:
        ls (list): The list in which the element occurs
        element (any): The element to search for in the list

    Returns:
        int: The last index of the element in the list
    """
    ls.reverse()
    i = ls.index(element)
    ls.reverse()
    return len(ls) - i - 1
