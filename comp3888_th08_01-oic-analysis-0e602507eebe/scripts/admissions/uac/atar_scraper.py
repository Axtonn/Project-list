"""
This script finds and records data from the UAC website.
"""
from typing import List
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import TimeoutException

from scripts.admissions.uac.uac_parser import (
    get_data_from_tab, input_institution_name, write_data)
from scripts.common.element_matcher import find_text


UAC_BASE_URL = "https://uac.edu.au/course-search/search/find-a-course-undergraduate?search="


def initialize_search_settings(driver) -> List[str]:
    """
    Sets up the search page of the UAC site for smoother scraping

    Args:
        driver (WebDriver): the driver linked to the UAC site.

    Returns:
        List: Lists all label names for institutions. Empty on failure.
    """
    wait = WebDriverWait(driver, timeout=2)

    wait.until(EC.visibility_of_element_located((By.TAG_NAME, 'body')))

    # Select all available institutions on UAC
    institutions_accordion = find_text(driver, "span", "Institutions")
    institutions_accordion.click()
    institute_checkboxes = driver.find_elements(By.CLASS_NAME, "inst-title")
    if not institute_checkboxes:
        return []

    available_institutes = [box.text for box in institute_checkboxes]

    # Test with random name with guaranteed results
    if not input_institution_name(driver, "b"):
        return []

    try:
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "perPage")))
    except TimeoutException:
        print("Could not find option to select results per page.")
        return []

    max_per_page_btns = driver.find_elements(By.CLASS_NAME, "perPage")
    if not max_per_page_btns:
        print("Could not find option to select max number of buttons.")
        return []
    max_per_page_btns[4].click()

    input_institution_name(driver, " ")
    return available_institutes


def switch_to_new_tab(driver, main_tab):
    """
    When a new tab is opened ensure that that tab is active.
    """
    tabs_handles = driver.window_handles
    for tab in tabs_handles:
        if tab != main_tab:
            driver.switch_to.window(tab)


def scrape(driver):
    """
    Full flow of fetching and scraping data from the UAC site.

    Args:
        driver (WebDriver): the driver connected to UAC site.

    Returns:
        bool: True on success. False otherwise.
    """
    main_tab = driver.current_window_handle
    wait = WebDriverWait(driver, timeout=2)

    print("Setting up the browser in the background...")
    institutions = initialize_search_settings(driver)
    if not institutions:
        print("Unable to use the UAC site as expected. Please review this script.")
        return False

    for institution in institutions:
        # Select the instition to limit search to just a single institution,
        # which have no more than 500 (max entries per page) entries
        wait.until_not(EC.visibility_of_element_located(
            (By.CLASS_NAME, "active-filters")))
        checkbox = find_text(driver, "label", institution)
        # The browser must have the element in view to click it.
        ActionChains(driver).move_to_element(checkbox).perform()
        wait.until(EC.element_to_be_clickable(checkbox))
        checkbox.click()

        # Locate all the course listings and parse them one by one.
        wait.until(
            EC.visibility_of_element_located((By.TAG_NAME, "article")))
        courses = driver.find_elements(By.TAG_NAME, 'article')
        for course in courses:
            course_link = course.find_element(By.TAG_NAME, "a")
            ActionChains(driver).move_to_element(course_link).perform()
            course_link.click()

            switch_to_new_tab(driver, main_tab)
            success, data = get_data_from_tab(driver)
            if success:
                write_data(data)
            driver.close()
            driver.switch_to.window(main_tab)

        wait.until(EC.visibility_of_element_located(
            (By.CLASS_NAME, "active-filters")))
        ActionChains(driver).move_to_element(checkbox).perform()
        checkbox.click()
    return True


if __name__ == "__main__":
    # Initialize driver
    print("Initializing driver...")
    options = ChromeOptions()
    options.add_argument("--headless=new")
    chromedriver = Chrome(options)
    chromedriver.get(UAC_BASE_URL)
    scrape(chromedriver)
    chromedriver.close()
