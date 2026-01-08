"""Access Workforce Australia site to mine data on jobs and relevant degrees.

This script connects to https://www.workforceaustralia.gov.au/individuals/jobs
to search for a current list of job vacancies. For each job, if it requires a
university degree (bachelor, master, phd, md), then it is recorded in
`data/oic_careers.db`.

To run the script, first run `python3 initialize_db.py` from the `scripts`
directory. Then, run `python3 workforce_gov_data_scraper.py`. This will run
Chrome as a headless browser. Each page of data takes 10-20s to parse.

"""

from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from scripts.common.element_matcher import extract_degree_requirements
from scripts.common.db_writer import DbWriter

WORKFORCE_URL = "https://www.workforceaustralia.gov.au/individuals/jobs/search"
JOB_NUM_PER_PAGE = 20


def extract_job_details():
    """
    Finds elements, if they exists, for data on degree requirements,
    job location, and pay.
    """
    # Wait for data load (as indicated by presence of job details card).
    WebDriverWait(driver, timeout=5).until(
        EC.presence_of_element_located((By.CLASS_NAME, "card-inner")))
    job_details = driver.find_elements(By.CLASS_NAME, "card-inner")
    if not job_details:
        return ([], None, None)

    job_requirements = extract_degree_requirements(
        job_details[0].get_attribute("innerHTML"))
    if not job_requirements:
        return ([], None, None)

    metadata = driver.find_element(
        By.XPATH, "//ul[contains(@class, 'job-info-metadata')]")
    locations = metadata.find_elements(By.XPATH, "//li[1]/span[2]")
    pays = metadata.find_elements(By.XPATH, "//li[2]/span[2]")
    return (
        job_requirements,
        locations[0].text if locations else None,
        pays[0].text if pays else None
    )


# Initialize driver
driver = Chrome()
driver.get(WORKFORCE_URL)
max_page_num = int(driver.find_element(
    By.XPATH, "//nav[@class='mint-pagination']//li[position()=last()-1]//span").text)

db = DbWriter()
JOB_NUM = 0
PAGE_NUM = 1
PAGE_LOADED = True

# Fetch data from each page of jobs.
while True:
    for i in range(JOB_NUM_PER_PAGE):
        if not PAGE_LOADED:
            break

        wait = WebDriverWait(driver, timeout=5)
        wait.until(EC.presence_of_element_located((
            By.XPATH, f"(//a[contains(@class, 'mint-link')])[{i+1}]")))

        jobs = driver.find_elements(
            By.XPATH, f"(//a[contains(@class, 'mint-link')])[{i+1}]")
        if not jobs:
            break
        job_title = jobs[0].text

        # Open link to details of the current job and extract data
        print(f"\rGetting data from job #{JOB_NUM:> 4} on pg{PAGE_NUM:< 4}: " +
              f"{job_title:.10}...".ljust(75), end="")
        driver.execute_script("arguments[0].click();", jobs[0])
        requirements, location, pay = extract_job_details()
        JOB_NUM += 1

        # Return to general results page.
        driver.back()

        if not requirements:
            continue

        res = db.execute(
            """INSERT INTO job_listing_raw(job_title, location, salary, source)
                VALUES (?, ?, ?, 'workforceaustralia.gov.au')""",
            (job_title, location, pay))

        if res is None:
            print("\rFailed to add new job listing entry.".ljust(75), end="")
            continue

        job_id = res.lastrowid
        for requirement in requirements:
            db.execute(
                """INSERT INTO job_degree_requirements_raw(degree, career)
                    VALUES (?, ?)""",
                (requirement, job_id))

    # Navigate to the next page.
    PAGE_NUM += 1
    if PAGE_NUM > max_page_num:
        break
    driver.get(f"{WORKFORCE_URL}?pageNumber={PAGE_NUM}")

    # Due to irregular population times, the pagination buttons often refer to
    # previous pages. This is not resolved by async `WebDriverWait`s for
    # elements to populate or be ready. Instead, navigate to each page and
    # refresh until it is populated with job data.
    for i in range(10):
        try:
            wait = WebDriverWait(driver, timeout=2)
            wait.until(EC.presence_of_element_located((
                By.XPATH, "//div[contains(text(), 'vacancies')]")))
            PAGE_LOADED = True
            break
        except TimeoutException:
            PAGE_LOADED = False
            driver.refresh()
            print(f"\rRetrying page {PAGE_NUM}".ljust(75), end="")


db.end_session()
driver.close()
