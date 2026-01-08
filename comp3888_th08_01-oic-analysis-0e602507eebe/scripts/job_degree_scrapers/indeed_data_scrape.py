"""
This is a script that can be run from the command line that queries 
`au.indeed.com` to extract jobs and their required degrees. The data is written
into a local database.
"""
import time
import random
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from scripts.common.element_matcher import find_text, extract_degree_requirements
from scripts.common.db_writer import DbWriter

INDEED_URL = "https://au.indeed.com"
KEYWORDS = ["bachelor", "degree", "master", "doctorate", "phd", "undegrad"]


def extract_job_details(driver):
    """
    Finds elements, if they exists, for data on degree requirements,
    job location, and pay.

    Args:
        driver (WebDriver): the driver that is running a headless browser
            with job details

    Returns:
        tuple: A tuple containing a list of job requirements as strings, job
            location or `None` if it was not found, and salary information or
            `None` if it was not found.
    """
    job_details = driver.find_elements(By.ID, "jobDescriptionText")
    if not job_details:
        return ([], None, None)
    job_requirements = extract_degree_requirements(
        job_details[0].get_attribute("innerHTML"))
    if not job_requirements:
        return ([], None, None)
    locations = driver.find_elements(
        By.XPATH, "//div[contains(@data-testid, 'companyLocation')]/div")
    pays = driver.find_elements(
        By.XPATH, "//h3[text()='Pay']/following-sibling::div//div[contains(text(), '$')]")

    return (
        job_requirements,
        locations[0].text if locations else None,
        pays[0].text if pays else None
    )


def prefilter_jobs(driver) -> None:
    """
    Navigates the indeed site to prepare a suitable search

    Args:
        driver (WebDriver): the driver that is running a headless browser
    """
    # Narrow search to only jobs in Australia.
    print("Filtering for Australian job listings")
    location_input = driver.find_element(By.ID, "text-input-where")
    location_input.send_keys("Australia")
    find_jobs_btn = find_text(driver, "button", "Find jobs")
    find_jobs_btn.click()

    # Further filter for jobs requiring at least an undergraduate level of study.
    print("Limiting results to only include jobs requiring a degree")
    education_btn = find_text(driver, "div", "Education level")
    education_btn.click()

    bachelors_check = find_text(driver, "span", "Bachelor")
    bachelors_check.click()

    masters_check = find_text(driver, "span", "Master")
    masters_check.click()

    phd_check = find_text(driver, "span", "Doctoral")
    phd_check.click()

    update_education_btn = find_text(driver, "span", "Update")
    update_education_btn.click()


def run_scraper(driver):
    """
    Retrieves data from "au.indeed.com" in order to write job titles and
    required degrees into a database. 

    Args:
        driver (WebDriver): the driver that is running a headless browser
    """

    db = DbWriter()
    next_page_btns = [None]
    job_num = 0
    jobs_extracted = 0
    while len(next_page_btns) > 0:
        popups = driver.find_elements(
            By.CLASS_NAME, "DesktopJobAlertPopup-heading")
        if len(popups) > 0:
            popups[0].find_element(By.XPATH, "following-sibling::*").click()

        if next_page_btns[0] is not None:
            next_page_btns[0].click()

        jobs = driver.find_elements(By.CLASS_NAME, "jcs-JobTitle")

        for job in jobs:
            # Close popups as they appear.
            popups = driver.find_elements(
                By.CLASS_NAME, "DesktopJobAlertPopup-heading")

            if len(popups) > 0:
                popups[0].find_element(
                    By.XPATH, "following-sibling::*").click()

            print(f"\rExtracting data from job #{job_num}".ljust(75), end="")

            job.click()
            requirements, location, pay = extract_job_details(driver)
            job_num += 1

            if not requirements:
                continue

            res = db.execute(
                """INSERT INTO job_listing_raw(job_title, location, salary)
                    VALUES (?, ?, ?)""",
                (job.text, location, pay))

            if res is None:
                print("\rFailed to add new job listing entry.".ljust(75), end="")
                continue

            job_id = res.lastrowid
            for requirement in requirements:
                db.execute(
                    """INSERT INTO job_degree_requirements_raw(degree, career)
                        VALUES (?, ?)""",
                    (requirement, job_id))
            jobs_extracted += 1

            print(f"\rAnalysed {job_num} jobs from Indeed.com. " +
                  f"Data extracted from {jobs_extracted}".ljust(10), end="")

        next_page_btns = driver.find_elements(
            By.XPATH, "//a[contains(@aria-label, 'Next Page')]")

        # Wait between 0 and 10 seconds to simulate "human" behaviour and
        # prevent cloudflare detection
        time.sleep(random.random() * 5)
        if job_num % 1000 == 0:
            time.sleep(15 + random.random() * 10)

    db.end_session()
    driver.close()


if __name__ == "__main__":
    # Initialize driver
    chromedriver = Chrome()
    chromedriver.get(INDEED_URL)
    # Use implicit wait strategy to avoid excessively flaky script.
    chromedriver.implicitly_wait(2)
    prefilter_jobs(chromedriver)

    run_scraper(chromedriver)
