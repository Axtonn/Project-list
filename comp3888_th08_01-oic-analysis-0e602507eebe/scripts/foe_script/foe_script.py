"""
https://www.abs.gov.au/statistics/classifications/australian-standard-classification-education-asced/2001#data-downloads
Downloads .xlsx file from website above (data/foe_raw.xlsx), 
extracts only the 4 digits narrow fields of educations along with its name
into to data/foe.csv file and dumps it in a database data/oic_careers.db.
"""
import sqlite3
import pandas as pd


def read_excel_file(file_path):
    """
    Reads an Excel file and returns the data as a DataFrame
    Args:
        file_path (str): the path of the .xlsx file to be read
    Returns:
        pandas.DataFrame: data read from the sheet "Table 2" of the Excel file, 
            containing records with columns 'Unnamed: 0', 'Narrow Fields', 
            'Unnamed: 2', and 'Unnamed: 3'
    """
    data_frame = pd.read_excel(file_path, sheet_name="Table 2", skiprows=5)
    print(f"Read Excel file from {file_path}")
    return data_frame


def extract_narrow_fields(data_frame):
    """
    Extracts 4 digits narrow fields of education from the DataFrame
    Args:
        data_frame (pandas.DataFrame): data read from the sheet "Table 2" of the 
            Excel file, containing records with columns 'Unnamed: 0', 
            'Narrow Fields', 'Unnamed: 2', and 'Unnamed: 3'
    Returns:
        pandas.DataFrame: a DataFrame containing only columns 'narrow fields' 
            and 'Unnamed: 2' from data_frame, with renamed columns 'code' and 'name' 
            respectively
    """
    narrow_fields = data_frame[["Narrow Fields", "Unnamed: 2"]].dropna()

    # Rename columns appropriately
    narrow_fields.columns = ["code", "name"]
    return narrow_fields


def output_to_csv(data_frame, path):
    """
    Inserts a DataFrame into a CSV file
    Args:
        data_frame (pandas.DataFrame): a DataFrame containing only columns 'narrow fields' 
            and 'Unnamed: 2' from data_frame, with renamed columns 'code' and 'name' 
            respectively
        path (str): the path of the .csv file to be written
    Returns:
        None
    """
    data_frame.to_csv(path, index=False)
    print(f"Data saved to {path}")


def create_foe_table(cursor):
    """
    Create a table 'foe' in a SQLite database using the cursor object given
    Args:
        cursor (sqlite3.connect.cursor): a cursor object to execute SQL commands
    Returns:
        None
    """
    try:
        cursor.execute("""
            CREATE TABLE foe (
                code TEXT PRIMARY KEY,
                name TEXT
            )
        """)
        print("'foe' table created")
    except sqlite3.OperationalError:
        print("'foe' table already exists")


def insert_into_database(data_frame, cursor):
    """
    Inserts a DataFrame into a SQLite database using the cursor object given
    Args:
        cursor (sqlite3.connect.cursor): a cursor object to execute SQL commands
    Returns:
        None
    """
    try:
        for _, row in data_frame.iterrows():
            cursor.execute("INSERT INTO foe (code, name) VALUES (?, ?)",
                           (row["code"], row["name"]))
        print("Data successfully inserted into the database")
    except sqlite3.IntegrityError:
        print("Data already exists in the database")


def main():
    """Main function"""

    file_name = "data/foe_raw.xlsx"
    output_csv_path = "data/foe.csv"

    narrow_fields = extract_narrow_fields(read_excel_file(file_name))

    output_to_csv(narrow_fields, output_csv_path)

    # Connect to SQLite database (or create it if it doesn't exist)
    db_path = "data/oic_careers.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Creates 'foe' table in the database (if it doesn't already exist)
    create_foe_table(cursor)

    # Inserts the narrow fields into the database (if they don't already exist)
    insert_into_database(narrow_fields, cursor)

    # Commit changes and close the connection
    conn.commit()
    conn.close()


if __name__ == '__main__':
    main()
