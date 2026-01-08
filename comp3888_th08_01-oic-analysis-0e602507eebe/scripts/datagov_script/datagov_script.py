import sqlite3
import pandas as pd


def create_institutions_table(con):
    """
    Create the 'institutions' table in the SQLite database if it doesn't exist.
    Args:
        con (sqlite3.Connection): a connection object to the SQLite database.
    """
    try:
        con.execute("""
            CREATE TABLE IF NOT EXISTS institutions(
                institution_id TEXT PRIMARY KEY,
                institution_name TEXT, 
                institution_type TEXT
            )
        """)
        print("Successfully created `institutions` table")
    except sqlite3.OperationalError as e:
        print(f"Error creating 'institutions' table: {e}")


def create_course_locations_table(con):
    """
    Create the 'course_locations' table in the SQLite database if it doesn't exist.
    Args:
        con (sqlite3.Connection): a connection object to the SQLite database.
    """
    try:
        con.execute("""
            CREATE TABLE IF NOT EXISTS course_locations(
                cl_id INTEGER PRIMARY KEY,
                course_id TEXT,
                location_name TEXT,
                city TEXT,
                state TEXT,
                FOREIGN KEY (location_name) REFERENCES locations(location_name),     
                FOREIGN KEY (course_id) REFERENCES courses(course_id)
            )
        """)
        print("Successfully created `course_locations` table")
    except sqlite3.OperationalError as e:
        print(f"Error creating 'course_locations' table: {e}")


def create_locations_table(con):
    """
    Create the 'locations' table in the SQLite database if it doesn't exist.
    Args:
        con (sqlite3.Connection): a connection object to the SQLite database.
    """
    try:
        con.execute("""
            CREATE TABLE IF NOT EXISTS locations(
                l_id INTEGER PRIMARY KEY,
                location_name TEXT,
                address_line_1 TEXT,
                city TEXT,
                state TEXT,
                postcode INTEGER
            )
        """)
        print("Successfully created `locations` table")
    except sqlite3.OperationalError as e:
        print(f"Error creating 'locations' table: {e}")


def create_courses_table(con):
    """
    Create the 'courses' table in the SQLite database if it doesn't exist.
    Args:
        con (sqlite3.Connection): a connection object to the SQLite database.
    """
    try:
        con.execute("""
            CREATE TABLE IF NOT EXISTS courses (
                institution_id TEXT,
                institution_name TEXT,
                course_id TEXT PRIMARY KEY, 
                course_name TEXT,
                foe1_broad_field TEXT,
                foe1_narrow_field TEXT,
                foe1_detailed_field TEXT,
                course_level TEXT,
                course_duration INTEGER,
                tuition_fee REAL,
                non_tuition_fee REAL,
                total_course_cost REAL,
                FOREIGN KEY (institution_id) REFERENCES institutions(institution_id)
            )
        """)
        print("Successfully created `courses` table")
    except sqlite3.OperationalError as e:
        print(f"Error creating 'courses' table: {e}")


def import_csv_to_sqlite(csv_file, table_name, con):
    """
    Imports data from a CSV file into a specified SQLite table.
    Args:
        csv_file (str): The path to the CSV file.
        table_name (str): The name of the table to insert data into.
        con (sqlite3.Connection): a connection object to the SQLite database.
    """
    dataframe = pd.read_csv(csv_file)
    dataframe.to_sql(table_name, con, if_exists='append', index=False)
    print(f"Successfully imported data from {csv_file} into {table_name} table.")


def main():
    # Connect to the SQLite database
    db_path = "data/oic_careers.db"
    con = sqlite3.connect(db_path)

    # Create the required tables
    create_institutions_table(con)
    create_course_locations_table(con)
    create_locations_table(con)
    create_courses_table(con)

    # Import data from CSV files into their respective tables
    try:
        import_csv_to_sqlite('data/datagov_cleaned/Institution_cleaned.csv', 'institutions', con)
        import_csv_to_sqlite('data/datagov_cleaned/CourseLocations_cleaned.csv', 'course_locations', con)
        import_csv_to_sqlite('data/datagov_cleaned/Locations_cleaned.csv', 'locations', con)
        import_csv_to_sqlite('data/datagov_cleaned/Courses_cleaned.csv', 'courses', con)
    except sqlite3.OperationalError as e:
        print(f"SQL Operational Error: {e}")
    else:
        print("All CSV files have been successfully imported.")
    finally:
        con.close()


if __name__ == '__main__':
    main()
