"""
Run the CategoriseCareers pipeline to automatically categorise all jobs from 
the `job_listing_raw` table into careers. 

100 entries are parsed at a time due to OpenAI's maximum document size. This
pipeline combines the results.
"""
import os
from pathlib import Path
from typing import Dict, List
from spacy_llm.util import assemble
from scripts.job_degree_scrapers.careers.database_helpers import (
    get_jobs, add_careers, create_careers_table)
from scripts.common.db_writer import DbWriter
# import the `CategoriseCareers` class so it is accessible by the pipeline
from scripts.job_degree_scrapers.careers.catergorise_careers import (
    CategoriseCareers
)


def run_pipeline(data: List[str]) -> Dict[str, List[str]]:
    """
    Run the CategoriseCareers pipeline to automatically categorise all jobs from 
    the `job_listing_raw` table into careers. 

    Args:
        data (List[str]): a list of string representing rows in from the 
                          `job_listing_raw` table. Each row must be of the
                          format "job_id, job_title"

    Returns:
        Dict: a dict of careers and all the raw `job_ids` they are associated
              with in the format of {career_name, [job_ids,]}
    """
    if not os.getenv("OPENAI_API_KEY", None):
        print("OPENAI_API_KEY env variable was not found.")
        return

    config_path = str(Path(__file__).parent) + "/categorise_careers.cfg"
    print("Assembling career categoriser pipe.")
    nlp = assemble(config_path)
    docs = nlp.pipe(data)

    careers = {}
    response_counter = 1
    for doc in docs:
        print("Parsing ChatGPT response #" + str(response_counter))
        for k, v in doc._.categories:
            if k in careers:
                careers[k].extend(v.split(","))
            else:
                careers[k] = v.split(",")
        response_counter += 1
    return careers


if __name__ == "__main__":
    db_writer = DbWriter()
    create_careers_table(db_writer.con)
    careers_dict = run_pipeline(get_jobs(db_writer.con))
    add_careers(db_writer.con, careers_dict)
