import sqlite3
from scripts.common.db_writer import DbWriter

con = sqlite3.connect(DbWriter.DB_PATH)
print("Connected to `oic_careers.db`")

# Create a table mapping jobs to location and salary
try:
    with con:
        con.execute("""
                    CREATE TABLE job_listing_raw(
                        job_id INTEGER PRIMARY KEY,
                        job_title TEXT NOT NULL,
                        location TEXT,
                        salary TEXT
                    )
                    """)
    print("Successfully created `job_listing_raw` table")
except sqlite3.OperationalError:
    print("The table 'job_listing_raw' already exists in the database. Skipping...")


try:
    with con:
        con.cursor().execute("""
                    ALTER TABLE job_listing_raw
                        ADD source text
                    """)
    print("Successfully Added `source` column to  `job_listing_raw` table")

    with con:
        res = con.cursor().execute("""
                    UPDATE job_listing_raw
                                   SET source="au.indeed.com"
                                   WHERE source IS NULL
                    """)
    print("updated all existing indeed entries with source as `au.indeed.com`")
except sqlite3.OperationalError:
    print("The column 'source' already exists in `job_listing_raw`. Skipping...")


# Create a table referencing the `job_listing_raw` table to map jobs with
# associated degree requirements
try:
    with con:
        con.execute("""
                    CREATE TABLE job_degree_requirements_raw(
                        degree_id INTEGER PRIMARY KEY,
                        degree TEXT NOT NULL,
                        career INTEGER,
                        FOREIGN KEY(career) REFERENCES job_listing_raw(job_id)
                    )
                    """)
    print("Successfully created `job_degree_requirements_raw` table")
except sqlite3.OperationalError:
    print("The table 'job_degree_requirements_raw' already exists in the database. Skipping...")


# Create a table `course_admission_requirements` to record the guaranteed,
# minimum, and median ATAR values for a particular course
try:
    with con:
        con.execute("""
                    CREATE TABLE course_admission_requirements(
                        course_id TEXT PRIMARY KEY,
                        admission_org TEXT 
                            CHECK(admission_org IN 
                            ('UAC', 'VTAC', 'QTAC', 'SATAC', 'TISC', 'UTAS')),
                        atar_guaranteed FLOAT,
                        atar_min_non_adj FLOAT,
                        atar_med_non_adj FLOAT,
                        atar_min_adj FLOAT,
                        atar_med_adj FLOAT,
                        admission_org_code TEXT,
                        FOREIGN KEY(course_id) REFERENCES courses(course_id)
                    )
                    """)
    print("Successfully created `course_admission_requirements` table")
except sqlite3.OperationalError:
    print("The table 'course_admission_requirements' already exists. Skipping...")

# Create a table `students` and `grades` to record student details
try:
    with con:
        con.execute("""
                    CREATE TABLE students(
                        student_id INTEGER PRIMARY KEY,
                        given_name TEXT,
                        surname TEXT,
                        country TEXT
                    )
                    """)
        con.execute("""
            CREATE TABLE examination_systems(
                exam_id TEXT PRIMARY KEY,
                grade_maximum FLOAT,
                country TEXT
            )
            """)
        con.execute("""
            CREATE TABLE grades(
                student_id INTEGER PRIMARY KEY,
                exam_id TEXT,
                score FLOAT,
                FOREIGN KEY(student_id) REFERENCES students(student_id)
                FOREIGN KEY(exam_id) REFERENCES examination_systems(exam_id)
            )
            """)

        con.execute("""
            CREATE TRIGGER student_grade_check
            BEFORE INSERT ON grades
            WHEN NEW.score < 0
                OR NEW.score > (
                    SELECT grade_maximum 
                    FROM examination_systems 
                    WHERE exam_id = NEW.exam_id)
            BEGIN
                SELECT RAISE(FAIL, "Invalid grade");
            END
            """)

    print("Successfully created `students` and `grades` table")
except sqlite3.OperationalError as e:
    print(e)
    print("Error creating `students` and `grades` table. Skipping...")

print('Successfully created database. Closing connection...')
con.close()
