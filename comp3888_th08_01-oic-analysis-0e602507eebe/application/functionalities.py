"""
Helper methods used for both careers and degrees in the GUI. Contains
functions to fetch FOEs and write data to an output JSON.
"""
import json
import tempfile
import sqlite3

from application.display_degrees import get_degree_dataframes
from application.career_rec.display_careers import get_career_dataframes
from scripts.common.db_writer import DbWriter

# Define a fixed temporary file path
temp_file_path = tempfile.NamedTemporaryFile(delete=False, suffix=".json").name


def fetch_foe_data():
    """Fetches all fields of educations from the database"""
    conn = sqlite3.connect(DbWriter.DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT code, name FROM foe")
    data = cursor.fetchall()
    conn.close()

    options = [(f"{name} ({code})", {'code': code, 'name': name})
               for code, name in data]
    return options


def fetch_foe_detailed_data():
    """Fetches all fields of educations (6-digit) from the database"""
    conn = sqlite3.connect(DbWriter.DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT code, name FROM foe_detailed")
    data = cursor.fetchall()
    conn.close()

    options = [(f"{name} ({code})", {'code': code, 'name': name})
               for code, name in data]
    return options


def generate_combined_output(input_json, additional_foe, additional_foe_detailed,
                             budget, student_details, top_ranked_au_uni,
                             should_prioritise_uncommon, randomness):
    json_foes = input_json["inputs"] if input_json else []
    extra_foe = additional_foe if additional_foe else []
    extra_foe_detailed = additional_foe_detailed if additional_foe_detailed else []
    grade = student_details["grade"] if student_details else None

    # Get degree dataframes
    degree_dataframes = get_degree_dataframes(
        json_foes + extra_foe + extra_foe_detailed, budget, top_ranked_au_uni, grade)

    # Get career dataframes
    career_dataframes = get_career_dataframes(
        json_foes + extra_foe + extra_foe_detailed,
        should_prioritise_uncommon, randomness)

    # Combine the dataframes into a single JSON output
    output_json = {"recommendations": []}

    for foe_code, (foe_name, rec_types) in degree_dataframes.items():
        recommendation = {"foe_code": foe_code, "courses": {}, "careers": []}
        recommendation["name"] = foe_name
        for rec_type, degrees in rec_types.items():
            recommendation["courses"][rec_type] = []

            for degree in degrees:
                if not degree or not degree[0]:
                    continue
                recommendation["courses"][rec_type].append({
                    "course_university": degree[0],
                    "course_name": degree[1],
                    "course_length": degree[2],
                    "course_total_cost": degree[3],
                    "atar_min_non_adj": degree[4],
                    "atar_med_non_adj": degree[5],
                    "atar_guaranteed": degree[6],
                    "admission_center": degree[7],
                    "admission_center_code": degree[8]
                })

        if foe_code in career_dataframes:
            salary = career_dataframes[foe_code][1]
            if len(salary) == 5:
                recommendation["salary_summary"] = {
                    "minimum": salary[0],
                    "q1": salary[1],
                    "median": salary[2],
                    "q3": salary[3],
                    "maximum": salary[4]
                }

            if career_dataframes[foe_code][2]:
                for career in career_dataframes[foe_code][2]:
                    recommendation["careers"].append({
                        "career_name": career[0],
                        "satisfaction": career[1],
                        "career_growth_2028": career[2],
                        "career_growth_2033": career[3],
                        "future_skill_shortage": career[4],
                    })

        output_json["recommendations"].append(recommendation)

    with open(temp_file_path, 'w') as fp:
        json.dump(output_json, fp, indent=4)

    return output_json, temp_file_path
