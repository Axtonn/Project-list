import sqlite3
import pandas as pd
from pandas import DataFrame
import csv
import numpy as np
from scripts.common.db_writer import DbWriter


def preprocess_data(filepath):
    """
    Import csv file and preprocess the parts in need.
    Args:
        filepath (String): the filepath to the csv file of the SEEK data.
    """
    with open(filepath, newline='') as csvfile:
        careerListRaw = list(csv.reader(csvfile))
    i = 0
    while i < len(careerListRaw):
        if(i > 0):
            #Clean number of reviews
            if(careerListRaw[i][5] != ''):
                careerListRaw[i][5] = int(careerListRaw[i][5].split(" ")[2])
            #Clean number of job openings
            if(careerListRaw[i][1] != ''):
                careerListRaw[i][1] = int(careerListRaw[i][1].replace(",", ''))
            #Clean job growth percentage
            if(careerListRaw[i][3] != ''):
                careerListRaw[i][3] = float(careerListRaw[i][3].strip("%"))
            #Clean salary
            if(careerListRaw[i][2] == 'N/A'):
                careerListRaw[i][2] = ''
            if(careerListRaw[i][2] != ''):
                careerListRaw[i][2] = int(careerListRaw[i][2].strip("$K"))*1000
            #Create job_id column
            careerListRaw[i].insert(0,i)
        i += 1

    #Remove header and leave data only
    careerListRaw.pop(0)
    return careerListRaw


def create_salaries_table(con):
    """
    Create the 'salaries' table in the SQLite database if it doesn't exist.
    Args:
        con (sqlite3.Connection): a connection object to the SQLite database.
    """
    try:
        con.execute("""
            CREATE TABLE IF NOT EXISTS salaries(
                job_id INTEGER PRIMARY KEY,
                job_name TEXT,
                job_num INTEGER, 
                salary INTEGER,
                job_growth FLOAT,
                satisfaction FLOAT,
                review_num INTEGER,
                job_field TEXT
            )
        """)
        print("Successfully created `salaries` table")
    except sqlite3.OperationalError as e:
        print(f"Error creating 'salaries' table: {e}")


def import_list_to_sqlite(jobList, table_name, con):
    """
    Imports cleaned data as a python array form, loads it to the salaries table on the database
    Args:
        jobList (list): The data to load, in the format of a python list.
        table_name (str): The name of the table to insert data into.
        con (sqlite3.Connection): a connection object to the SQLite database.
    """
    df = DataFrame(data=np.array(jobList),
                   index=np.arange(len(jobList)),
                   columns=['job_id','job_name','job_num','salary','job_growth','satisfaction','review_num','job_field'])
    df.to_sql(table_name, con, if_exists='append', index=False)
    try:
        con.execute("""
            UPDATE salaries
                SET salary = NULL
                WHERE salary = ''
                        """)
        con.commit()
    except sqlite3.OperationalError as e:
        print(f"Error handling empty string data in 'salaries' table: {e}")
    print(f"Successfully imported data from SEEK into {table_name} table.")


def main():
    # Connect to the SQLite database
    db_path = DbWriter.DB_PATH
    filepath = "data/career_related/SEEK_career_advice_jobs_only.csv"
    con = sqlite3.connect(db_path)

    # Create the required table
    create_salaries_table(con)

    # Import data from CSV file into its table
    jobList = preprocess_data(filepath)
    try:
        import_list_to_sqlite(jobList, 'salaries', con)
    except sqlite3.OperationalError as e:
        print(f"SQL Operational Error: {e}")
    else:
        print("All CSV files have been successfully imported.")
    finally:
        con.close()


if __name__ == '__main__':
    main()