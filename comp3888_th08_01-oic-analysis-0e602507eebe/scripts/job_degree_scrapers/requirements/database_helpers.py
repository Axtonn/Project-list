"""
Helper functions for database read and write operations to support
degree_requirement cleaning
"""
from sqlite3 import Connection, OperationalError
from typing import Dict, List


SELECT_DEGREES_STATEMENT = """
    SELECT foe, GROUP_CONCAT(DISTINCT course_name) 
    FROM (SELECT SUBSTR(foe1_narrow_field, 1, 4) as foe, course_name FROM courses)
    GROUP BY foe
    HAVING foe IS NOT NULL
    """

SELECT_REQUIREMENTS_STATEMENT = """
    SELECT degree_id, degree, career FROM job_degree_requirements_raw
"""


def get_all_degrees(database_connection: Connection) -> Dict[str, List[str]]:
    """
    Fetches all degree and course names and groups them with ones that have the
    same primary FOE. Degrees without a listed primary FOE are ignored.

    Params:
        database_connection (Connection): A `sqlite3` connection to the database
            with course data.

    Returns:
        Dict: A dictionary that maps field of educations with degrees, with the 
              FOE string as the key, and a list of degree names as the value.
    """

    print("Getting courses...")
    results = database_connection.execute(SELECT_DEGREES_STATEMENT, ())

    return {res[0]: res[1].split(",") for res in results}


def get_degree_requirements(database_connection: Connection) -> List[tuple]:
    """
    Fetches all degree requirements, including the degree id, degree name,
    and job id

    Params:
        database_connection (Connection): A `sqlite3` connection to the database
            with course data.

    Returns:
        List: A list of all degree requirements as tuples of (degree_id, degree, job_id)
    """

    print("Getting degree requirements...")
    results = database_connection.execute(SELECT_REQUIREMENTS_STATEMENT, ())

    return results.fetchall()


def career_id_from_raw_req(database_connection: Connection, raw_req_id: str):
    """
    Fetches the career ID of the cleaned career associated with a particular
    degree requirement listing.

    Args:
        database_connection (Connection):  A `sqlite3` connection to the 
            database with job data.
        raw_req_id (str): the ID of the degree requirement listing from the
            `job_degree_requirements_raw` table.

    Returns:
        tuple[int]: A tuple of length 1 if there is a career associated with
            the listing. The first and only element of the tuple is the integer
            ID of the career. Otherwise, returns `None`.
    """
    try:
        with database_connection:
            result = database_connection.cursor().execute("""
                SELECT c.career_id 
                FROM 
                    (careers AS c INNER JOIN job_listing_raw AS jl
                     ON c.career_id = jl.career_id)
                        INNER JOIN 
                    job_degree_requirements_raw AS d 
                        ON d.career = jl.job_id 
                WHERE d.degree_id = ?           
                """, (raw_req_id,))
        return result.fetchone()
    except OperationalError as e:
        print("Unable to fetch career ids:", e)
        return None


def create_degree_requirements_table(database_connection: Connection):
    """
    Creates a new `degree_requirements` table in the database if it does
    not already exist.

    Args:
        database_connection (Connection): connection to SQLite database

    Returns:
        boolean: True if a table was successfully created. False otherwise.
    """
    try:
        with database_connection:
            database_connection.execute(
                """
                CREATE TABLE IF NOT EXISTS degree_requirements (
                    requirement_id INTEGER PRIMARY KEY,
                    foe_code TEXT,
                    raw_requirement_id INTEGER,
                    career_id INTEGER,
                    matched_text TEXT,
                    matched_weight FLOAT,
                    FOREIGN KEY(foe_code) REFERENCES foe(code),
                    FOREIGN KEY(raw_requirement_id) REFERENCES job_degree_requirements_raw(degree_id),
                    FOREIGN KEY(career_id) REFERENCES careers(career_id)
                )""")
        return True
    except OperationalError:
        print("Unable to create new `degree_requirements` table")
        return False


def add_degree_requirement(database_connection: Connection, requirements: List[tuple]):
    """
    Inserts any number of new degree requirement entries into the
    `degree_requirements` table.

    Args:
        database_connection (Connection): _description_
        requirements (List[tuple]): The requirements to insert in the format of
            `(foe, raw_requirement_id, matched_text, matched_weight, career_id)`

    Returns:
        bool: True if all rows are successfully inserted. False otherwise.
            No rows are inserted if any fail.
    """
    try:
        with database_connection:
            database_connection.cursor().executemany("""
                INSERT INTO degree_requirements(
                    foe_code, raw_requirement_id, matched_text, matched_weight, career_id)
                VALUES (?, ?, ?, ?, ?)                    
                """, requirements)
        return True
    except OperationalError:
        print("Unable to add new rows to the degree_requirements table")
        return False
