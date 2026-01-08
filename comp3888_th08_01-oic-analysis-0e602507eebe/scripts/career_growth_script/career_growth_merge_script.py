# The module performs text preprocessing by removing stopwords and focusing on key content words 
# to enhance the accuracy of string matching. It then utilizes the fuzz.ratio() function from the 
# fuzzywuzzy library to compute a similarity score between cleaned job titles from both the 
# job growth and careers tables. Based on the computed similarity, similar job titles are 
# merged into the careers table if the similarity score exceeds 80, adhering to the requirements 
# outlined in the JIRA Task description.

# Additionally, if no matching career name is found between the careers and degree requirements 
# tables, new entries are added to the degree_requirements table accordingly.

import sqlite3
import pandas as pd
from fuzzywuzzy import fuzz
from nltk.corpus import stopwords
import nltk
from scripts.common.db_writer import DbWriter

nltk.download('stopwords')

def clean_text(text):
    """
    Cleans the given text by removing stopwords and converting to lowercase.

    Parameters:
        text (str): The text to be cleaned.

    Returns:
        str: The cleaned text with stopwords removed and lowercase conversion.
    """
    if text is None:  # Handle None values
        return ""
    
    stop_words = set(stopwords.words('english'))
    words = text.lower().split()  # Convert text to lowercase and split into words
    cleaned_words = [word for word in words if word not in stop_words]  # Remove stopwords
    return " ".join(cleaned_words)  # Join cleaned words back into a string

def load_data(db_path: str):
    """
    Loads data from the database into Pandas dataframes.

    Parameters:
        db_path (str): The absolute path to the database file.

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]: 
            A tuple containing growth_data, careers, and degree_requirements DataFrames.
    """
    conn = sqlite3.connect(db_path)
    growth_data = pd.read_sql_query("SELECT * FROM growth_data", conn)
    careers = pd.read_sql_query("SELECT * FROM careers", conn)
    degree_requirements = pd.read_sql_query("SELECT * FROM degree_requirements", conn)
    conn.close()
    return growth_data, careers, degree_requirements

def clean_job_titles(growth_data: pd.DataFrame, careers: pd.DataFrame):
    """
    Cleans the job titles in the growth_data and careers tables by removing stopwords and 
    converting them to lowercase.

    Parameters:
        growth_data (pd.DataFrame): The DataFrame containing growth_data job titles.
        careers (pd.DataFrame): The DataFrame containing careers job titles.

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: 
            A tuple containing the cleaned growth_data and careers DataFrames.
    """
    growth_data['clean_name'] = growth_data['occupation'].apply(clean_text)
    careers['clean_name'] = careers['career_name'].apply(clean_text)
    return growth_data, careers

def fuzzy_match_jobs(growth_data: pd.DataFrame, careers: pd.DataFrame, threshold: int = 90):
    """
    Performs fuzzy matching between the job titles in growth_data and careers tables.

    Parameters:
        growth_data (pd.DataFrame): The DataFrame containing growth_data job titles.
        careers (pd.DataFrame): The DataFrame containing careers job titles.
        threshold (int): The similarity score threshold for considering a match (default is 90).

    Returns:
        list: A list of tuples representing matches between growth_data and careers.
    """
    matches = []
    for _, growth_row in growth_data.iterrows():
        best_match = None
        best_score = 0

        for _, career_row in careers.iterrows():
            score = fuzz.ratio(growth_row['clean_name'], career_row['clean_name'])  # Compute similarity score
            if score > best_score:
                best_score = score
                best_match = career_row

        if best_score >= threshold:  # Assume match if score >= threshold
            matches.append((growth_row, best_match, True))  # Match found
        else:
            matches.append((growth_row, None, False))  # No match found
    return matches

def merge_and_update(matches: list, careers: pd.DataFrame, degree_requirements: pd.DataFrame, start_index: int = 14324):
    """
    Merges matched jobs and updates the careers and degree_requirements tables.

    Parameters:
        matches (list): A list of matched job titles between growth_data and careers.
        careers (pd.DataFrame): The careers DataFrame to be updated.
        degree_requirements (pd.DataFrame): The degree_requirements DataFrame to be updated.
        start_index (int): The starting index for new entries in the degree_requirements table (default is 14324).

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: 
            A tuple containing the updated careers and degree_requirements DataFrames.
    """
    for growth_row, career_row, is_match in matches:
        if is_match:
            # Update existing career with job from growth_data
            if len(growth_row['occupation']) < len(career_row['career_name']):
                careers.loc[careers['career_id'] == career_row['career_id'], 'career_name'] = growth_row['occupation']
        else:
            # Add new career entry
            new_career_id = careers['career_id'].max() + 1
            careers = pd.concat([careers, pd.DataFrame([{
                'career_id': new_career_id,
                'career_name': growth_row['occupation'],
                'clean_name': growth_row['clean_name']
            }])], ignore_index=True)

            # Add entry to degree_requirements
            degree_requirements = pd.concat([degree_requirements, pd.DataFrame([{
                'requirement_id': start_index,
                'foe_code': 'Manual Entry Needed',
                'raw_requirement_id': None,
                'career_id': new_career_id,
                'matched_text': None,
                'matched_weight': 0.5
            }])], ignore_index=True)
            start_index += 1

    return careers, degree_requirements

def save_data(db_path: str, careers: pd.DataFrame, degree_requirements: pd.DataFrame):
    """
    Saves the updated careers and degree_requirements DataFrames back to the SQLite database.

    Parameters:
        db_path (str): The absolute path to the database file.
        careers (pd.DataFrame): The updated careers DataFrame.
        degree_requirements (pd.DataFrame): The updated degree_requirements DataFrame.

    Returns:
        None
    """
    conn = sqlite3.connect(db_path)
    careers.to_sql('careers', conn, if_exists='replace', index=False)
    degree_requirements.to_sql('degree_requirements', conn, if_exists='replace', index=False)
    conn.close()

def process_job_matching(db_path: str):
    """
    Executes the job matching process by loading data, cleaning job titles, performing fuzzy matching,
    merging data, and saving the updated careers and degree_requirements back to the database.

    Parameters:
        db_path (str): The absolute path to the database file.

    Returns:
        None
    """
    # Load the data
    growth_data, careers, degree_requirements = load_data(db_path)

    # Clean the job titles
    growth_data, careers = clean_job_titles(growth_data, careers)

    # Perform fuzzy matching
    matches = fuzzy_match_jobs(growth_data, careers)

    # Merge the data and update careers and degree_requirements tables
    careers, degree_requirements = merge_and_update(matches, careers, degree_requirements)

    # Save the updated data back to the database
    save_data(db_path, careers, degree_requirements)

    print("Merging complete, updated careers and degree_requirements saved.")

if __name__ == "__main__":
    process_job_matching(DbWriter.DB_PATH)
