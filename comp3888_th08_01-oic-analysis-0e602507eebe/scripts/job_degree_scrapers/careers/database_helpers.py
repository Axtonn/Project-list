"""
Helper functions for database read and write operations to support
careers cleaning
"""
from sqlite3 import Connection, OperationalError
from typing import List, Dict

SELECT_JOBS_STATEMENT = """
    SELECT job_id, job_title 
    FROM job_listing_raw
"""

MAX_GPT_TOKEN_LENGTH = 8192


def get_jobs(database_connection: Connection) -> List[str]:
    """
    Fetches all job listings with id and title as a string.

    Params:
        database_connection (Connection): A `sqlite3` connection to the 
            database with job data.

    Returns:
        List: A list of all degree requirements as a string in the format of 
              "job_id | job_title", or an empty string if it fails.
    """

    print("Fetching jobs...")
    results = database_connection.execute(SELECT_JOBS_STATEMENT, ())

    if results is None:
        print("There was an issue fetching requirements.")
        return ""

    lines = [f"{res[0]}, {res[1]}" for res in results.fetchall()]

    job_inputs = []
    for i in range(0, len(lines), 100):
        job_inputs.append("\n".join(lines[i:i + 100]))
    return job_inputs


def create_careers_table(database_connection: Connection) -> bool:
    """
    Creates a new `careers` table in the database if it does not already exist.

    Args:
        database_connection (Connection): connection to SQLite database

    Returns:
        bool: True if a table was successfully created. False otherwise.
    """
    try:
        with database_connection:
            database_connection.execute(
                """
                CREATE TABLE IF NOT EXISTS careers (
                    career_id INTEGER PRIMARY KEY,
                    career_name TEXT UNIQUE
                )""")
        return True
    except OperationalError:
        print("Unable to create new `careers` table")
        return False


def update_job_listing_raw_with_career_id(database_connection: Connection) -> bool:
    """
    Adds a new column to the `job_listing_raw` table that references the
    `careers` table as a foreign key. 

    Args:
        database_connection (Connection): connection to SQLite database

    Returns:
        bool: True if the insertion of a new column was successful. False
                 otherwise.
    """
    try:
        with database_connection:
            database_connection.execute("""
                DROP TABLE IF EXISTS new_job_listing_raw 
                """)
            database_connection.execute("""
                CREATE TABLE new_job_listing_raw(
                    job_id INTEGER PRIMARY KEY,
                    job_title TEXT NOT NULL,
                    location TEXT,
                    salary TEXT,
                    source TEXT,
                    career_id INTEGER,
                    FOREIGN KEY(career_id) REFERENCES careers(career_id)
                )
                """)
            database_connection.execute("""
                INSERT INTO new_job_listing_raw(
                    job_id, job_title, location, salary, source)
                SELECT job_id, job_title, location, salary, source 
                FROM job_listing_raw
                """)
            database_connection.execute("""
                DROP TABLE job_listing_raw
                """)
            database_connection.execute("""
                ALTER TABLE new_job_listing_raw RENAME TO job_listing_raw
                """)
        return True
    except OperationalError as e:
        print("Unable to add new foreign key constraint to `job_listing_raw`", e)
        return False


def add_careers(database_connection: Connection, careers: Dict[str, List[str]]) -> bool:
    """
    For all the listed careers, add them into the `careers` table. Then fill in
    `career_id` column in the `job_listing_raw` table with the id of the row
    with the corresponding `career_name` (as listed in the `careers` dict).

    Args:
        database_connection (Connection): connection to SQLite database
        careers (Dict[str, str]): Dictionary containing entries of 
                                  {career_names: [raw_job_ids]}

    Returns:
        bool: True if the operation was successful. False otherwise.
    """
    try:
        with database_connection:
            database_connection.cursor().executemany("""
                INSERT INTO careers(career_name)
                VALUES (?)                    
                """, [(k,) for k in careers])
    except OperationalError as e:
        print("Unable to add new rows to the careers table", e)
        return False

    update_job_listing_raw_with_career_id(database_connection)

    update_statement = """
                UPDATE job_listing_raw
                    SET career_id = c.career_id
                FROM (SELECT career_id 
                        FROM careers 
                        WHERE career_name = ?) AS c
                WHERE job_listing_raw.job_id IN ({})        
                """
    try:
        with database_connection:
            for career_name, raw_job_ids in careers.items():
                database_connection.cursor().execute(
                    update_statement.format(",".join("?"*len(raw_job_ids))),
                    (career_name,  *raw_job_ids))
    except OperationalError as e:
        print("Unable to update job_listing_raw table: ", e)
        return False
    return True
