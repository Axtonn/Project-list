"""This module contains functions which query the database and return degree information."""

from typing import Optional
import math
import sqlite3
import gradio as gr
from scripts.common.db_writer import DbWriter
import gradio as gr

ATAR_MAX = 99.95


def get_degrees(foe, budget=700, top_ranked_au_uni=None, grade=None, min_grade=0):
    """
    Retrieves institution name, course name and course duration
    from the SQLite database.
    The entries are sorted by university rankings.

    Args:
        foe (str): The narrow or detailed field of education code.

    Returns:
        list: A 2D list containing institution names, course names, and course durations.
    """

    filters = {"foe": f"{foe}%", "budget": budget,
               "top": top_ranked_au_uni, "grade": grade, "min": min_grade}

    grade_template = """
        AND ((guaranteed > :min AND guaranteed <= :grade) 
             OR (med > :min AND med <= :grade ))"""

    budget_template = """
        AND total_course_cost <= :budget"""

    template = f"""
        SELECT i.institution_name, course_name, course_duration, total_course_cost,
               ROUND(car.atar_min_non_adj, 2), ROUND(car.atar_med_non_adj, 2) AS med,
               car.atar_guaranteed AS guaranteed, car.admission_org, car.admission_org_code
        FROM institutions i
        INNER JOIN courses c ON i.institution_id = c.institution_id
        LEFT JOIN course_admission_requirements car ON c.course_id = car.course_id
        WHERE {"foe1_detailed_field" if len(foe) == 6 else "foe1_narrow_field"} LIKE :foe
        {grade_template if grade else ""}
        {budget_template if budget else ""}
        AND i.institution_id IN (
            SELECT institution_id
            FROM institutions
            WHERE ranking is NOT NULL
            ORDER BY ranking ASC
        {"LIMIT :top)" if top_ranked_au_uni else ")"}
        AND course_level LIKE 'Bachelor%'
        ORDER BY ranking ASC;
        """

    with sqlite3.connect(DbWriter.DB_PATH) as con:
        cursor = con.cursor()
        cursor.execute(template, filters)
        rows = cursor.fetchall()

    for i, row in enumerate(rows):
        rows[i] = list(row)

    return rows


def get_degree_dataframes(foe_list, budget, top_ranked_au_uni, grade: Optional[float]):
    """
    Prepares a dictionary of FOEs and their corresponding degree recommendations. This
    can optionally factor in the student's ATAR results.

    Args:
        foe_list (any): A list of FoEs and their corresponding names.
        budget (any): The maximum total course cost the user is willing to pay.
        top_ranked_au_uni (any): The number of universities to return, ordered
            from highest to lowest ranking. `None` to return all unis.
        grade (Optional[float]): The student's grades as an ATAR result. The
            value must be between 0 and `ATAR_MAX`=99.95.

    Returns:
        Dict: A dictionary of FOE codes and their corresponding 
            `(name, recommendations)` tuples. `recommendations` itself is a
            dictionary containing lists of degree details for "target" and 
            "reach" universities.
    """
    degree_dataframes = {}

    if grade:
        reach_grade = grade + ((ATAR_MAX - grade) * math.log10(grade)) / 4
        grade = grade + 1
    else:
        reach_grade = None

    for foe in foe_list:
        if foe["code"] in degree_dataframes:
            continue

        target_degrees = get_degrees(
            foe["code"], int(budget) * 1000,
            int(top_ranked_au_uni) if top_ranked_au_uni else None, grade)

        reach_degrees = []
        if grade:
            reach_degrees = get_degrees(
                foe["code"], int(budget) * 1000,
                int(top_ranked_au_uni) if top_ranked_au_uni else None,
                reach_grade, grade)

        degree_dataframes[foe["code"]] = (
            foe["name"], {"target": target_degrees, "reach": reach_degrees})

    return degree_dataframes


def show_degrees_with_filters(input_json, budget, top_ranked_au_uni,
                              additional_foe, additional_foe_detailed,
                              student_details):
    """
    Displays a list of suitable degrees with the foes in `input_json` and
    additional foes in `additional_foe`

    Args:
        input_json: File test inputs
        budget: The maximum budget for the student
        top_ranked_au_uni: Whether to filter only for the highest ranked unis
        additional_foe: Additional foes added from the display
        grade: The predicted grade for the student
    """

    @gr.render(inputs=[input_json, budget, top_ranked_au_uni,
                       additional_foe, additional_foe_detailed,
                       student_details])
    def display_degree_fields(json, budget, top_ranked_au_uni,
                              extra_foe, extra_foe_detailed, student):
        json_foes = json["inputs"] if json else []
        extra_foe = extra_foe if extra_foe else []
        extra_foe_detailed = extra_foe_detailed if extra_foe_detailed else []
        grade = student["grade"] if student else None

        all_degree_dataframes = get_degree_dataframes(
            json_foes + extra_foe + extra_foe_detailed, budget, top_ranked_au_uni, grade)
        for code, (name, degree_data) in all_degree_dataframes.items():
            with gr.Accordion(label=code + " " + name, open=False):
                gr.DataFrame(value=degree_data["target"], label="Target courses",
                             headers=["University", "Course Name", "Length (Weeks)", "Total Course Cost",
                                      "Minimum ATAR", "Median ATAR", "Guaranteed ATAR", "Admission Centre",
                                      "Center Code"])
                if not degree_data["reach"]:
                    continue
                gr.DataFrame(value=degree_data["reach"], label="Reach courses — Achievable with Additional Work",
                             headers=["University", "Course Name", "Length (Weeks)", "Total Course Cost",
                                      "Minimum ATAR", "Median ATAR", "Guaranteed ATAR", "Admission Centre",
                                      "Center Code"])


def update_student_details(input_json: any):
    """
    Based on the student ID provided in `input_json`, retrieves a student's
    name, exam score, and type of exam taken.
    """

    if "student_id" not in input_json:
        return None

    student_id = input_json["student_id"]

    template = """
    SELECT s.given_name, s.surname, g.score, g.exam_id
    FROM students AS S 
        INNER JOIN grades AS g ON s.student_id = g.student_id
    WHERE s.student_id = ?
    """

    with sqlite3.connect(DbWriter.DB_PATH) as con:
        cursor = con.cursor()
        cursor.execute(template, (student_id,))

    first, last, grade, exam = cursor.fetchone()

    return {"name": f"{first} {last}", "grade": grade, "exam_type": exam, "id": student_id}
