# Datamining career development and future growth data
# Using pandas, sqlite3
# By: Zijin Wang SID: 500461859
# Date: 25/08/24
#
# References:
# - Unviersity of Victoria Employment Forcasting Model
# - Jobs and skills dataset
#
# Jobs and skill projection data - Numericalised MODEL based
import os
import sqlite3
import pandas as pd
from helper.request_url import download_file
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.common.by import By

# Target URL for datamining
URL = 'https://www.jobsandskills.gov.au/data/employment-projections'

# Target files
DATA_FILE_NAME = './scripts/job_growth_script/growth_data_numerical.xlsx'
DATA_CSV_NAME = './data/Skills Priority List data (ANZSCO 4) - 2023.csv'
DB_PATH = "./data/oic_careers.db"

# Chromedriver initialisation
options = ChromeOptions()
options.add_experimental_option("detach", True)
driver = Chrome(options=options)
driver.get(URL)

# Looking at all linked texts in html with download
try:
    dl_linked_text = driver.find_elements(By.LINK_TEXT, 'Download')
except NoSuchElementException:
    print("No Linked Text elements can be found... Exiting..")
    driver.quit()
    quit()

# Filtering for dl button
temp_dl = None
for dl in dl_linked_text:
    if (dl.get_attribute('href') and '.xlsx' in dl.get_attribute('href') and
            'Download' in dl.text):
        temp_dl = dl
        break


# Check if the data URL is valid
if temp_dl is None:
    print("Data URL can not be found from the given source... Exiting.. ")
    driver.quit()
    quit()


# Request for file data
download_file(temp_dl.get_attribute('href'), DATA_FILE_NAME)
driver.quit()

# Data processing using Pandas
# col_names specifies all read column names in original file
col_names = ['occ_Level', 'national_future_demand', 'code', 'occupation', 'skill',
             '2023_employment_level', '2028_employment_level' '2033_employment_level',
             '2028_numerical', '2028_job_growth', '2033_numerical', '2033_job_growth']
dataframe = pd.read_excel(DATA_FILE_NAME, sheet_name="Detailed Occupation Projections",
                          skiprows=3, names=col_names, index_col=False)

# Processing data for 4 digit occupation codes, occupation and percentage growth
# Processing - removing unwanted/unimportant columns. Preseved comumns include
#              4 digit code, Occupation Name, 2028 growth % and 2033 growth %
# Numerical dataset has in values under 1001, these are categorised summaries, these do
# not match the generalised dataset. Therefore drop every row that has a Code value under 1001
dataframe = dataframe[['code', 'occupation',
                       '2028_job_growth', '2033_job_growth']]
dataframe['code'] = dataframe['code'].astype(int)
dataframe = dataframe.drop(dataframe[dataframe.code < 1001].index)

# Read Generalised Data, following similar approach as above
# csv column names in original file
col_names_csv = ['code', 'occupation', 'national_future_demand', 'driver', 'national_shortage_raiting',
                 'NSW', 'VIC', 'QLD', 'SA', 'WA', 'TAS', 'NT', 'ACT']
dataframe_csv = pd.read_csv(DATA_CSV_NAME, names=col_names_csv,
                            index_col=False, skiprows=1)
# Omit data that is not required, preserving Code, National Future Demand and
# National shortage rating.
dataframe_csv = dataframe_csv[[
    'code', 'national_future_demand', 'national_shortage_raiting']]

# Merge dataframes by name, preserving all Codes present in numerical data (larger)
# In case of missing data from generalised data (Smaller) NaN is added to dataframe
dataframe_merged = dataframe.merge(dataframe_csv, how='left')

# Connect to SQLite database
conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# Make SQL table from merged dataframe
dataframe_merged.to_sql("growth_data", con=conn,
                        if_exists='replace', index=False)

# Cleanup resources
os.remove(DATA_FILE_NAME)
