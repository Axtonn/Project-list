import random
import gradio as gr
import pandas as pd
import numpy as np

from scripts.common.db_writer import DbWriter


def recommend_careers_for_foe(database, foe, prioritise_uncommon=True, randomness=0):
    """
    Retreives the names of careers that are associated with particular FOEs in
    order of how representative they are for that FOE.
    See `documentation/career_recommendation.md` for more details.

    Args:
        database (Connection): A connection to the database with careers data.
        foe (str): The narrow field of education code.
        prioritise_uncommon (bool): Whether the algorithm should fetch careers
            that are not as common
        randomness (float): The degree of randomness with which to fetch career
            results. 0 is deterministic. 1 is very random.

    Returns:
        list: The names of careers for the given `foe`.
    """
    filters = {}

    # Extract the career name, growth, and shortage data from the database.
    template = """
        -- Prepare to merge recommendations with satisfaction ratings
        -- as a join on tables to avoid duplicates when merging without grouping
        SELECT rec.name, 
			SUM(salaries.satisfaction * salaries.review_num)
              /SUM(salaries.review_num) as job_satisfaction,
			rec.growth_2028, rec.growth_2033, rec.shortage, rec.weight
        FROM (
        SELECT 
          cars.career_id AS id,
          cars.career_name AS name,
		  cars."2028_job_growth" AS growth_2028,
          cars."2033_job_growth" AS growth_2033,
          cars.national_shortage_raiting AS shortage,
        """

    # Calculate the weighting of each career for this FOE.
    template += "SUM(req.matched_weight)/rarities.rarity" if prioritise_uncommon else "SUM(req.matched_weight)"
    template += "* IFNULL(growth_multiplier, 1) * IFNULL(shortage_multiplier, 1)"

    # Multiply by a randomisation value between 1 and 1 + `randomness`.
    template += "* (1 + (random_between(0,:rand_max))) AS weight"
    filters["rand_max"] = randomness

    # Identify relationship between career names and their degree requirements,
    # including the growth and shortage multiplier.
    # See `documentation/career_recommendation.md` for more details.
    template += """
        FROM ((
            (
              -- Find weightings for how related a career is to an FOE.
              degree_requirements AS req INNER JOIN careers AS c
                ON req.career_id = c.career_id
            ) AS car LEFT JOIN
            (
              -- Calculate weight multipliers based on projected job growth.
              SELECT occupation,
                "2028_job_growth",
                "2033_job_growth",
                national_shortage_raiting,
                CASE national_shortage_raiting
                  WHEN "Shortage" THEN 1.5
                  WHEN "Regional Shortage" THEN 1.25
                  ELSE 1
                  END AS shortage_multiplier,
                -- Use relative ranking of 2033 growth to calculate multiplier
                CAST(ROW_NUMBER() OVER growth AS FLOAT) / COUNT(*) OVER() + 0.5
                  AS growth_multiplier 
              FROM growth_data
              WINDOW growth AS (ORDER BY "2033_job_growth")
            ) AS g ON car.career_name = g.occupation
          ) AS cars
        """

    # Create mapping between each career and how common it is in the database.
    if prioritise_uncommon:
        template += """
            INNER JOIN (SELECT
                career_id, COUNT(*) as rarity
                FROM degree_requirements
                GROUP BY career_id) AS rarities
            ON rarities.career_id = cars.career_id
            """
    # End the recommendation selection statement.
    template += """)
        WHERE req.foe_code = :foe_code
        GROUP BY c.career_name) AS rec"""

    # Join the recommendation with salary data, ranking by weight.
    template += """
        LEFT JOIN salaries ON salaries.careers_id = rec.id
        GROUP BY rec.id
        ORDER BY weight DESC, rec.id ASC
        LIMIT 5
        """
    filters["foe_code"] = foe

    with database as con:
        con.create_function('random_between', 2, random.uniform)
        cursor = con.cursor()
        cursor.execute(template, filters)
        rows = cursor.fetchall()

    return rows


def summarize_salaries(database, foe: str):
    """
    Fetches the relevant salaries associated with an FOE and calculates the
    quartiles for those careers.

    Args:
        database (any): Connection to a SQLite database 
        foe (str): The FOE code to calculate a salary summary for

    Returns:
        List[str] | np.array[float]: A list of "N/A" (length 5) if there are
            no associated salaries. Otherwise, an array of 
            [`min`, `quartile 1`, `med`, `quartile 3`, `max`] salaries, as
            calculated via the `np.quantile` function

    """
    salary_template = """
        SELECT AVG(salary)
        FROM (
            SELECT c.career_id FROM 
                degree_requirements AS req INNER JOIN careers AS c
                    ON req.career_id = c.career_id
                    WHERE foe_code = ?
                GROUP BY c.career_id
                HAVING SUM(req.matched_weight) >= 0.25
        ) AS car
        INNER JOIN salaries as s ON s.careers_id = car.career_id
        WHERE s.weak_link != 2
          AND s.salary IS NOT NULL
		GROUP BY car.career_id
		ORDER BY AVG(s.salary) ASC
        """

    with database as con:
        con.create_function('random_between', 2, random.uniform)
        cursor = con.cursor()
        cursor.execute(salary_template, (foe,))
        salaries = [salary[0] for salary in cursor.fetchall()]

    if not salaries:
        return ['N/A', 'N/A', 'N/A', 'N/A', 'N/A']

    quartiles = np.quantile(salaries, [0, 0.25, 0.5, 0.75, 1])
    return np.round(quartiles)


def get_career_dataframes(foe_list, prioritise_uncommon, add_randomness):
    """
    Fetches a recommendation and displays the recommended careers. Duplicate
    FOEs in the FOE list are ignored

    Args:
        foe_list (List): Foe list with both the code and the name of the foe
        prioritise_uncommon (bool): Whether to make the algorithm prioritise
            uncommon careers
        add_randomness (bool): Whether to fores the algorithm to become
            non-deterministic

    Returns:
        dict: A dict mapping FOE codes with their names and matched careers
    """
    career_dataframes = {}
    for foe in foe_list:
        if foe["code"] in career_dataframes:
            continue

        careers = recommend_careers_for_foe(
            DbWriter().con, foe["code"], prioritise_uncommon, add_randomness)

        salary_summary = summarize_salaries(DbWriter().con, foe["code"])

        career_dataframes[foe["code"]] = (foe["name"], salary_summary, careers)

    return career_dataframes


def show_career_recommendations(input_json, should_prioritise_uncommon,
                                randomness, additional_foe, additional_foe_detailed):
    """
    Create a gradio component that displays recommended careers.

    Args:
        input_json: the input file with FOE data.
        additional_foe: user-chosen FOE from the GUI.
    """

    @gr.render(inputs=[input_json, should_prioritise_uncommon, randomness,
                       additional_foe, additional_foe_detailed])
    def show_career_fields(json, prioritise_uncommon, add_randomness,
                           extra_foe, extra_foe_detailed):
        json_foes = json["inputs"] if json else []
        extra_foe = extra_foe if extra_foe else []
        extra_foe_detailed = extra_foe_detailed if extra_foe_detailed else []

        all_career_dataframes = get_career_dataframes(
            json_foes + extra_foe + extra_foe_detailed, prioritise_uncommon, add_randomness)
        for code, (name, salaries, career_data) in all_career_dataframes.items():
            with gr.Accordion(label=code + " " + name, open=True):
                # Display salary data as a table, if it is available.
                if len(salaries) == 5:
                    gr.DataFrame(
                        value=[salaries],
                        label="Typical salaries in this field (AUD)",
                        headers=["Minimum", "First Quartile", "Median", "Third Quartile", "Maximum"])

                # Display suitable careers where it is available.
                if career_data:
                    career_dataframe = pd.DataFrame(
                        [career[:-1] for career in career_data],
                        columns=["Careers", "Job Satisfaction", "Growth by 2028 (%)",
                                 "2033_job_growth (%)", "Skill Shortage"])
                    career_styled = career_dataframe.style \
                        .format(precision=2, na_rep="",
                                subset=["Job Satisfaction", "Growth by 2028 (%)", "2033_job_growth (%)"])
                    gr.DataFrame(value=career_styled,
                                 label="Careers you may be suited for")
