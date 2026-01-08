"""
Helper functions for locating and reading data from UAC website.
"""
import re
from typing import List, Tuple, Dict
from bs4 import BeautifulSoup, PageElement
import numpy as np
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC

from scripts.admissions.admission_center import AdmissionCenter
from scripts.admissions.atar_data_helper import (
    check_admission_requirements_exist, find_matching_course, insert_admission_requirement)


NO_ATAR_IGNORE = ["NN", "NP", "-"]
"""
UAC uses multiple tags to signify reason for lack of data. We ignore courses
where the data is not provided for the following reasons:
    `–`: data is not available
    `NN`: Unavailable (other)
    `NP`: Not provided by institution
"""

NO_ATAR_KEEP = ["NC", "N/A", "<5", "NO", "NS", "NR",]
"""
ATAR no data reason tags that are kept as `NULL` in the database
    `<5`: less than 5 ATAR-based offers were made.
    `N/A`: no offers were made on the basis of ATAR.
    `NC`: new course
    `NO`: Entry on other criteria
    `NR`: No reportable profile
    `NS`: No Semester 1 offers
"""


def input_institution_name(driver, name: str) -> bool:
    """
    Force the driver to navigate to the search bar and input `name` as the
    search query.

    Args:
        driver (WebDriver): Driver connected to the UAC site
        name (str): the value to input into as a search query

    Returns:
        bool: True on success. False on failure.
    """
    try:
        search_div = driver.find_element(By.CLASS_NAME, "search-bar")
        search_input = search_div.find_element(By.TAG_NAME, "input")
    except NoSuchElementException:
        print("Could not locate the search bar element")
        return False
    if search_input.get_attribute("value"):
        search_input.clear()
    search_input.send_keys(name)
    return True


def handle_atar_table(atar_table_html) -> List[None | float]:
    """
    Reads in the html of the UAC ATAR table outputs a list of 4 ATAR values
    from the table in order of 
    1. Min ATAR with no adjustments
    2. Median ATAR with no adjustments
    3. Min ATAR with adjustements
    4. Median ATAR with adjustments

    Values in the list are possibly `None` if no data was available. If data
    was not available for any subcourses, for reasons in the `NO_ATAR_IGNORE`
    list, then an empty list is returned.

    Args:
        atar_table_html: the outerHTML of the ATAR table object

    Returns:
        List: Returns a list of 4 ATAR values.
    """
    atar_soup = BeautifulSoup(atar_table_html, "html.parser")
    atar_table: List[PageElement] = atar_soup.find_all(name="td")
    row_num = int(len(atar_table) / 6)  # The table  has 6 cells in a row.
    atars = []
    for row in range(row_num):
        row_atar = []
        for i in range(6):
            # Skip the highest ATARs, which are the 3rd and 6th elements.
            if (i+1) % 3 == 0:
                continue

            current_atar = atar_table[row*6 + i].get_text().strip()

            # Ignore rows without data due to the `NO_ATAR_IGNORE` case,
            # but track rows that have no data for some other reason.
            if current_atar in NO_ATAR_IGNORE:
                break
            if current_atar in NO_ATAR_KEEP:
                row_atar.append(None)
                continue

            # Parse ATAR value but reject any not in range
            try:
                atar_val = float(current_atar)
                if atar_val > 99.95 or atar_val < 0:
                    break
                row_atar.append(atar_val)
            except ValueError:
                break

        if len(row_atar) == 4:
            atars.append(row_atar)

    if not atars:
        return []

    # Extract the smallest min ATARs for all rows,
    atar_arr = np.array(atars, dtype=float)
    if np.all(np.isnan(atar_arr)):
        return [None, None, None, None]
    med_atar = np.nanmedian(atar_arr, axis=0)
    min_atar = np.nanmin(atar_arr, axis=0)
    return [None if np.isnan(min_atar[0]) else min_atar[0],
            None if np.isnan(med_atar[1]) else med_atar[1],
            None if np.isnan(min_atar[2]) else min_atar[2],
            None if np.isnan(med_atar[3]) else med_atar[3]]


def get_data_from_tab(driver) -> Tuple[bool, Dict[str, any]]:
    """
    Given a tab for course data, find all the pertinent details and record
    them in a dictionary.

    Args:
        driver (WebDriver): A driver on a tab with UAC course details

    Returns:
        Tuple[bool, Dict]: A tuple were the first element is whether this
            operation was successful. The second element is a dictionary
            filled with the scraped data
    """
    wait = WebDriverWait(driver, timeout=2)
    wait.until(EC.visibility_of_element_located((By.TAG_NAME, 'body')))

    data = {"code": None, "guaranteed_atar": None}
    # Find CRICOS provider number.
    try:
        cricos_num = driver.find_element(
            By.CSS_SELECTOR, "p:has(.c-prov-num)")
    except NoSuchElementException:
        print("Could not locate CRICOS number.")
        return (False, {})
    cricos_num = cricos_num.text.split(": ")[1]
    data["provider"] = cricos_num.split(" ")[0]

    # Find course title.
    try:
        data["course_name"] = driver.find_element(
            By.CSS_SELECTOR, ".course-title").text
    except NoSuchElementException:
        print("Could not locate course name.")
        return (False, {})

    # Find UAC course code.
    try:
        data["code"] = driver.find_element(
            By.CSS_SELECTOR, ".course-code").text
    except NoSuchElementException:
        pass

    # Find ATAR min and median values.
    try:
        atar_data = driver.find_element(
            By.CSS_SELECTOR, "#atarDataTable > tbody")
        atars = handle_atar_table(atar_data.get_attribute("outerHTML"))
        if not atars:
            return (False, {})
        data["atars"] = atars
    except NoSuchElementException:
        print("No ATAR data found.")
        return (False, {})

    # Find guaranteed ATAR value, under the title "Guaranteed ATAR"
    guaranteed_atar = driver.find_elements(
        By.XPATH, "//p//*[contains(text(), 'Guaranteed ATAR')]/..")
    # Else, find guaranteed ATAR under the title "Guaranteed selection rank".
    if not guaranteed_atar:
        guaranteed_atar = driver.find_elements(
            By.XPATH, "//p//*[contains(text(), 'Guaranteed selection rank')]/..")
    if guaranteed_atar:
        result = re.search(
            r"(?<=: )\d{1,2}(\.\d{1,2})?", guaranteed_atar[0].text)
        data["guaranteed_atar"] = float(result.group()) if result else None

    return True, data


def write_data(data: Dict[str, any], ask_input=False) -> bool:
    """
    Writes the scraped data into the database. Entries that already exist in
    the database (as checked by collisions in (`provider`, `course_name`) or)
    in `course_id` are ignored but treated as successes.

    If no course could be automatically found, then this script prompts the
    runner of the script to manually find and enter the CRICOS codes (as a
    comma-separated list). Blank input is considered a "skip".

    Args:
        data (Dict[str, any]): Scraped data.

    Returns:
        bool: Whether the data was sucessfully inserted.
    """
    print(f"Adding {data['provider']} - {data['course_name']} to database...")
    if check_admission_requirements_exist(AdmissionCenter.UAC, data["code"]):
        print("\tThe entry already exists. Skipping")
        return True
    matching_course_ids = find_matching_course(
        data["provider"], data["course_name"])

    if not matching_course_ids and not ask_input:
        return False

    if not matching_course_ids and ask_input:
        print("\tCould not find a matching course.\a", end=" ")
        user_codes = input("Enter a comma-separated list of CRICOS codes: ")

        if not user_codes.strip():
            print("\tNo input entered. Skipping.")
            return False
        matching_course_ids = [code.strip() for code in user_codes.split(",")]

    for course_id in matching_course_ids:
        success = insert_admission_requirement(
            course_id, AdmissionCenter.UAC, data["code"],
            data["guaranteed_atar"], data["atars"])
        print(f"\tcourse ID {course_id}: {'success' if success else 'fail'}.")

    return True
