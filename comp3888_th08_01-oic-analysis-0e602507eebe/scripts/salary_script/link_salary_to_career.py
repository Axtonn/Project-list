import spacy
import sqlite3
import numpy as np
from pandas import DataFrame
# from scripts.common.db_writer import DbWriter

#Load large size model
nlp = spacy.load("en_core_web_lg")

# Load medium size model if large model takes too long
# nlp = spacy.load("en_core_web_md")


def find_matching_link(salaries_names, careers_names):
    """
    Using the spacy module, this function analyzes the word similarity
    between the job titles of the 2 tables: 'careers' and 'salaries.'

    Each of the rows in 'salaries' is linked to a row in 'careers' table
    that have the highest similarity.
    Args:
        salaries_names (list): List of the job titles from the 'salaries' table
        careers_names (list): List of the job titles from the 'careers' table
    Returns:
        foreign_keys (list): List of lists, each of which contains the index of entry
                            with the highest similarity, alongside with the similarity scores
                            to use when highlighting low-similarity entries.
    """
    foreign_keys = []
    i = 0
    while(i<len(salaries_names)):
        j = 0
        s_name = nlp(salaries_names[i])
        highest = [-1,-1]
        while(j<len(careers_names)):
            if(salaries_names[i] in careers_names[j] or careers_names[j] in salaries_names[i]):
                highest = [j,1]
                break
            c_name = nlp(careers_names[j])
            similarity = s_name.similarity(c_name)
            if(similarity > highest[1]):
                highest[0] = j
                highest[1] = similarity
            j += 1
        foreign_keys.append(highest)
        print(salaries_names[i], highest)
        i += 1
    return foreign_keys
            


def fetch_career_names(conn, table_name, column_name):
    """
    Given the name of the target table and column, this function fetches data of a single column
    and returns a list of the content.
    Args:
        conn (sqlite3.Connection): a connection object to the SQLite database.
        table_name: name of the table that containts the data we want to fetch
        column_name: name of the column that contains the data we want to fetch
    Returns:
        job_names_list: List of the content of the column
    """
    cursor = conn.cursor()
    job_names_list = []
    if(table_name == "careers" and column_name == "career_name"):
        template = """
            SELECT career_name from careers
            """
    elif(table_name == "salaries" and column_name == "job_name"):
        template = """
            SELECT job_name from salaries
            """
    else:
        print("Invalid table/column combination!")
        return
    cursor.execute(template)
    result = cursor.fetchall()

    job_names_list = [row[0] for row in result]

    return job_names_list


def add_columns(conn):
    """
    Creates additional columns 'careers_id(foreign key)' and 'weak_link' to the 'salaries' table on the database
    Args:
        conn (sqlite3.Connection): a connection object to the SQLite database
    """
    try:
        # conn.execute("""
        #     DROP TABLE salaries
        # """)

        conn.execute("""
            ALTER TABLE salaries
                ADD COLUMN careers_id INTEGER REFERENCES careers(career_id)
        """)
        conn.execute("""
            ALTER TABLE salaries
                ADD COLUMN weak_link INTEGER
        """)
        print("Successfully created additional columns in `salaries` table")
    except sqlite3.OperationalError as e:
        print(f"Error creating additional columns in 'salaries' table: {e}")


def fill_columns(conn, foreign_keys):
    """
    Fills in the additional columns based on the matched information between 'salaries' and 'careers'
    Args:
        conn (sqlite3.Connection): a connection object to the SQLite database
        foreign_keys: List returned from function 'find_matching_link()'
    """
    #Create list that will hold numbers to sit on the db
    data_fill = []
    i = 0
    while i < len(foreign_keys):
        buffer = []
        buffer.append(foreign_keys[i][0] + 1)
        if(foreign_keys[i][1] == 0):
            buffer.append(2)
        elif(foreign_keys[i][1] < 0.3):
            buffer.append(1)
        else:
            buffer.append(0)
        data_fill.append(buffer)
        i += 1
    #Update database row by row
    i = 0
    while i<len(data_fill):
        try:
            conn.execute("""
                UPDATE salaries
                    SET careers_id = ?, weak_link = ?
                    WHERE job_id = ?
                         """, (data_fill[i][0], data_fill[i][1], i+1))
            conn.commit()
            print(data_fill[i][0])
        except sqlite3.OperationalError as e:
            print(f"Error filling data in 'salaries' table: {e}")
        i += 1
    print("Successfully linked careers table and salaries table")


def main():
    #Connect to the SQLite database
    # db_path = DbWriter.DB_PATH
    db_path = "data/oic_careers.db"
    conn = sqlite3.connect(db_path)

    #Create lists that hold job titles
    salaries_names = fetch_career_names(conn, 'salaries', 'job_name')
    careers_names = fetch_career_names(conn, 'careers', 'career_name')

    """
    Analyse similarity and create links between tables
    The function 'find_matching_link()' uses the spacey module, comparing each rows of tables 'careers' and 'salaries'
    Due to the large number of rows, the whole process takes alot of time.
    As an alternative option to save time, there is a file that has the calculted results saved. See line 157.
    """
    foreign_keys = find_matching_link(salaries_names, careers_names)
    print(foreign_keys)

    """
    Utility lines to save time:
    Calculate the new rows that have to be inserted by a pre-calculated result saved at data/career_related/sample_links.txt
    This txt file contains the output of foreign_keys that is produced and returend by the function 'find_matching_links'
    """
    # links_calculated = "data/career_related/sample_links.txt"
    # f = open(links_calculated, 'r')
    # foreign_keys = f.readline().strip().split("],")
    # i = 0
    # while i<len(foreign_keys):
    #     foreign_keys[i] = foreign_keys[i].strip(" []").split(",")
    #     foreign_keys[i][0] = int(foreign_keys[i][0])
    #     foreign_keys[i][1] = float(foreign_keys[i][1])
    #     i += 1

    #Add additional columns to 'salaries' table    
    add_columns(conn)

    #Populate the added columns with relevant data
    fill_columns(conn,foreign_keys)

    conn.close()



if __name__== '__main__':
    main()