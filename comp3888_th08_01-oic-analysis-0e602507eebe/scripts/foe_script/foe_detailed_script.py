"""
https://www.abs.gov.au/statistics/classifications/australian-standard-classification-education-asced/2001#data-downloads
Downloads .xlsx file from website above (data/foe_raw.xlsx), 
extracts the 6 digits detailed fields of educations along with its name
into to data/foe_detailed.csv file and dumps it in a database table called foe_detailed.
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
            skipping first 6 lines to get "Detailed Fields" as a column header
    """
    data_frame = pd.read_excel(
        file_path, sheet_name="Table 2", skiprows=6)
    print(f"Read Excel file from {file_path}")
    return data_frame


def extract_detailed_fields(data_frame):
    """
    Extracts 6 digits detailed fields of education from the DataFrame
    Args:
        data_frame (pandas.DataFrame): data read from the sheet "Table 2" of the 
            Excel file
    Returns:
        pandas.DataFrame: a DataFrame containing the detailed foe fields with its corresponding narrow fields
    """
    detailed_fields = data_frame[[
        "Detailed Fields", "Unnamed: 3"]].dropna()

    # Rename columns appropriately
    detailed_fields.columns = ["code", "name"]

    # Add a new column 'narrow_foe' with the first 4 digits of the 'code'
    detailed_fields["narrow_foe"] = detailed_fields["code"].apply(lambda x: str(x)[
                                                                  :4])
    return detailed_fields


def output_to_csv(data_frame, path):
    """
    Inserts a DataFrame into a CSV file
    Args:
        data_frame (pandas.DataFrame): a DataFrame containing the detailed foe fields with its corresponding narrow fields
        path (str): the path of the .csv file to be written
    Returns:
        None
    """
    data_frame.to_csv(path, index=False)
    print(f"Data saved to {path}")


def create_foe_detailed_table(cursor):
    """
    Create a table 'foe_detailed' in a SQLite database using the cursor object given
    Args:
        cursor (sqlite3.connect.cursor): a cursor object to execute SQL commands
    Returns:
        None
    """
    try:
        cursor.execute("""
            CREATE TABLE foe_detailed (
                code TEXT PRIMARY KEY,
                name TEXT,
                narrow_foe TEXT,
                FOREIGN KEY (narrow_foe) REFERENCES foe(code)
            );
        """)
        print("'foe_detailed' table created")
    except sqlite3.OperationalError:
        print("'foe_detailed' table already exists")


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
            cursor.execute("INSERT INTO foe_detailed (code, name, narrow_foe) VALUES (?, ?, ?)",
                           (row["code"], row["name"], row["narrow_foe"]))
        print("Data successfully inserted into the database")
    except sqlite3.IntegrityError:
        print("Data already exists in the database")


def main():
    """Main function"""

    file_name = "data/foe_raw.xlsx"
    output_csv_path = "data/foe_detailed.csv"

    detailed_fields = extract_detailed_fields(read_excel_file(file_name))

    output_to_csv(detailed_fields, output_csv_path)

    # Connect to SQLite database (or create it if it doesn't exist)
    db_path = "data/oic_careers.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Creates 'foe_detailed' table in the database (if it doesn't already exist)
    create_foe_detailed_table(cursor)

    # Inserts the narrdetailedow fields into the database (if they don't already exist)
    insert_into_database(detailed_fields, cursor)

    # Commit changes and close the connection
    conn.commit()
    conn.close()


if __name__ == '__main__':
    main()
