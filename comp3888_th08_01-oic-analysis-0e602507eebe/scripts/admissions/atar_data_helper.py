"""
Common helper methods that fetch and write data for ATAR scripts
"""
from typing import List, Optional, Tuple
from scripts.admissions.admission_center import AdmissionCenter
from scripts.common.db_writer import DbWriter


def check_admission_requirements_exist(admission_center: AdmissionCenter,
                                       internal_code: Optional[str] = None,
                                       cricos_code: Optional[str] = None):
    """
    Finds near exact matches (case insensitive) of courses in the database with
    the same provider ID and course name as given. At least one of 
    `internal_code` or `cricos_code` must be provided. 

    Args:
        admission_center (AdmissionCenter): The organisation hosting admission
            information for this course.
        internal_code (str | None): The internal code used by the organisation.
        cricos_code (str | None): The CRICOS code for the course. This can be
            used instead of the internal code if no internal code is used by
            the admission center.

    Returns:
        bool: True if the data already exists in the table. False otherwise.
    """
    database_conn = DbWriter()

    if not internal_code and not cricos_code:
        return False

    if cricos_code:
        template = """
            SELECT 1
            FROM course_admission_requirements
            WHERE course_id = ?
            """
        params = (cricos_code,)
    else:
        template = """
            SELECT 1
            FROM course_admission_requirements
            WHERE admission_org = ? AND
                admission_org_code = ? 
            """
        params = (admission_center, internal_code)

    cursor = database_conn.execute(template, params)
    if not cursor:
        return False
    return bool(cursor.fetchone())


def find_matching_course(provider: str, course_name: str) -> List[Tuple[str]]:
    """
    Finds near exact matches (case insensitive) of courses in the database with
    the same provider ID and course name as given.

    Args:
        provider (str): CRICOS provider ID.
        course_name (str): The name of the course.

    Returns:
        List[Tuple[str]]: A list of `course_ids`. Empty list if none exists.
    """
    database_conn = DbWriter()
    template = """
        SELECT course_id
        FROM courses
        WHERE institution_id = ? AND
            course_name LIKE ?
        """
    cursor = database_conn.execute(template, (provider, course_name))
    if not cursor:
        return []

    return [datum[0] for datum in cursor.fetchall()]


def insert_admission_requirement(course_id: str, admission_center: AdmissionCenter,
                                 center_code: Optional[str], guaranteed: Optional[float],
                                 atars: List[Optional[float]]):
    """
    Inserts a single entry into the `course_admission_requirements` database.
    If the `course_id` already exists in the table, then no action is completed.

    Args:
        course_id (str): The CRICOS id for this admission requirement entry.
        admission_center (AdmissionCenter): The type of admissions centre
        center_code (str): The internal code used by the admissions centre for
            the course. This is value may or 
        guaranteed (float | None): Guaranteed entry ATAR, if it exists
        atars (List[float | None]): List of four ATARs in order of 
            minimum accepted ATAR (non-adjusted), median accepted ATAR (non-
            adjusted), minimum accepted ATAR (adjusted), median accepted ATAR
            (adjusted). Each of the ATARs in the list may be `None`.

    Returns:
        bool: True on success. False otherwise.
    """

    database_conn = DbWriter()
    template = """
        INSERT INTO course_admission_requirements(
            course_id,
            admission_org,
            atar_guaranteed,
            atar_min_non_adj,
            atar_med_non_adj,
            atar_min_adj,
            atar_med_adj,
            admission_org_code
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(course_id) DO NOTHING
        """
    cursor = database_conn.execute(
        template,
        (course_id, admission_center, guaranteed, *atars, center_code))
    return bool(cursor)
