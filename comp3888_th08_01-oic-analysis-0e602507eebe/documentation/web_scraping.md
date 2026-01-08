<!-- vscode-markdown-toc -->

<!-- vscode-markdown-toc-config
	numbering=false
	autoSave=true
	/vscode-markdown-toc-config -->
<!-- /vscode-markdown-toc -->

# Web Scraping

**Table of Contents**

- [Web Scraping](#markdown-header-web-scraping)
  - [Job and Education Requirements Data](#markdown-header-job-and-education-requirements-data)
    - [Limitations](#markdown-header-limitations)
    - [Alternate solutions](#markdown-header-alternate-solutions)
    - [Cleaning the Data](#markdown-header-cleaning-the-data)
    - [Future Work](#markdown-header-future-work)
  - [Degree ATAR Data](#markdown-header-degree-atar-data)
    - [Data Complexities](#markdown-header-data-complexities)
    - [Limitations](#markdown-header-limitations-1)

## Job and Education Requirements Data

Within Australia there are no public databases that link careers to education
and study areas. There are several potential solutions that can help address
this shortage of data.

The chosen solution was to scrape public listings of jobs from sites like
[Indeed.com](scripts/job_degree_scrapers/indeed_data_scrape.py) and
[Workforce Australia](scripts/job_degree_scrapers/workforce_gov_data_scraper.py)
to populate our database with jobs. Because employers will often highlight
education requirements in the job listings, this data allows connections to be
made between job titles and degrees. We can then leverage existing connection
between degrees and FOEs to fully connect our input (FOEs) to our output
(careers).

In general, the process of web scraping involves using an automated browser,
`selenium`, to access the job listings. Then, it will select each listing to
access the detailed job information. From there, it picks out the salary, and
location (if applicable), as well as phrases containing mentions of bachelor's,
master's, or PhDs and inserts the job with its data into the database.

The two scripts currently available are

- [indeed_data_scrape](scripts/job_degree_scrapers/indeed_data_scrape.py)
- [workforce_gov_data_scraper](scripts/job_degree_scrapers/workforce_gov_data_scraper.py)

### Limitations

Although this solution addresses the dearth of data in this area, it does pose a
few issues. For one, due to the nature the sites chosen for web-scraping, the
data quality varies. There is no standardized naming of jobs, and the
requirements for each job are often listed in wildly different ways. This
presents a challenge in cleaning the data into a usable state.

Additionally, web scraping can be very flaky. Websites change their structure
very frequently. Web-scrapers rely heavily on the structure being consistent
across uses. This means that the work completed in these scrapers may become
outdated very quickly. That said, this was the chosen solution for addressing
data gaps because it capitalizes on existing resources. This eliminates the need
for the team to gather primary data.

Finally, web scraping also can expose organizations to more legal risk. Web
scraping in Australia is generally legal provided that the data is publicly
accessible (e.g. it does not require an account to access), does not contain
personal information (e.g. names and ages of people), and if it is proprietary
data, it is not used for commercial purposes. To our best knowledge, our
solutions do operate under these assumptions. However, the team does not have
much legal expertise. We highly recommend that the OIC team consult a legal
expert.

### Alternate solutions

**Identifying careers and degrees from sources like LinkedIn**, where
individuals list their education background as well as their positions in
various careers. The benefits of this solution are that careers on LinkedIn
reflect more aspiration long-term goals than job listings from the chosen sites.
Further, the tie between careers and degrees could much clearer. While not all
professions are equally represented on sites like LinkedIn, it is a reasonably
large database that would suit the purposes of an initial phase project like
this one. Although this solution would be technically the most useful, it was
rejected for legal reasons. Web scraping would not be legal in the case of
LinkedIn as the data in question is not publicly accessible. Should OIC wish to
pursue this solution in the future, direct collaboration with LinkedIn may be
necessary to gain commercial access to their data.

**2019-2020 Education and Employment Data**. The ABS periodically publishes
anonymized data on individuals, their education, career, salary, and other
metrics. We considered using this as a source instead of web-scraping. This
would provide cleaned and reliable data to use. However, we decided to focus
more on web-scraping as the ABS data is fairly high-level. The careers, for
instance are generalized to career fields like “Health” or “Society and
culture”. While there may be some useful insights from this data, it is not
granular enough for the purposes of this project.

### Cleaning the Data

Full details can be found in [`documents/career_cleaning`](career_cleaning)

### Future Work

The work here can be extended to more sources of data in the future. While
Indeed and Workforce Australia do illustrate a proof-of-concept, more source and
make the dataset more robust.

## Degree ATAR Data

To recommend degrees that suit a student's academic needs, we need data on
entrance requirements for courses across different universities. By law, the
statistics of minimum, median, and maximum ATARS accepted into are course must
be publicly available.This means that we are guaranteed to be able to access
this information (if it exists) for all courses.

Australian university admissions are handled by
[6 admissions centers](https://bitbucket.org/comp3888_th08_01/oic-analysis/src/d7bf09bf49efcb2ef521fe190901c2552ec512e9/scripts/admissions/admission_center.py#scripts/admissions/admission_center.py-7):

- QTAC (QLD)
- SATAC (SA and NT)
- TISC (WA)
- UAC (NSW)
- UTAS (TAS)
- VTAC (VIC)

The courses offered at Australian universities are split among these centers.
Unfortunately, none provide a public cleaned dataset of ATAR requirements, and
each has their own website with unique structuring. Therefore, in order to
retrieve the data we need, we employed web-scraping.

For each course, we collected data to fill out a new table,
`course_admission_requirements`, which has a 1 to optional 1 relationship with
the courses table:

- Guaranteed ATAR: float or NULL
- Minimum ATAR: float or NULL
- Median ATAR: float or NULL
- CRICOS CODE: TEXT Foreign key
- Admission System: ENUM
- Admission system code: text (can be used later to direct users to the original
  listing by generating urls with the code)
- Maximum ATAR is **NOT** collected currently as it was determined
  [not to be useful for recommendations](/documentation/degree_recommendation.md#grades)
  based on grade.

### Data Complexities

The data that we are using as a comprehensive list of courses is
[from CRICOS](/documentation/data.md#cricos-courses). CRICOS assigns each course
a unique course code. However, this code is not always used by the admissions
centers. Although the centers usually note the CRICOS Provider Number of the
course's host university, they use they own internal ID codes to track courses.
(Note: UTAS is an exception to this generalisation and does provide clear links
between internal and CRICOS codes.)

Our solution is to scrape each course and try to match them with entries in the
database by matching the exact name to one in the database.

Alternate solutions we considered include:

- Re-fetch all entries in the `courses` table from webscraping: This would
  bypass the need to match names in UAC and CRICOS course names. Meanwhile it
  would be fairly trivial to fetch most other necessary details like course
  cost. However, this would be a lot of repeated work, especially considering
  that the admission center website data changes too frequently to be a reliable
  source.
- Finding the correct course by using the search functions on admission centers
  to search for the course name and university combination. While this would let
  us use the existing name matching functions of the admission centers, it is
  not a reliable way to find all degrees as slight variations in the naming
  could return no results.

An additional complexity is that some courses, even at the same uni have the
same name. This is often due to differences in course duration or course
location. For instance, "Bachelor of Software Engineering at RMIT" on the UAC
site seems to just be 3 different course plans for the same outcome and ATAR. We
decided to simplify this by linking the first instance of this course to all
instances of it in the CRICOS data as it is difficult to determine which is
which from name and course duration alone. This is a reasonable concession to
make because all instances of "Bachelor of Software Engineering at RMIT" are
connected on the UAC site.

### Limitations

- Each of the admission Centers in Australia has their own website that needs a
  separate script. We have only implemented scraping for UAC courses. This means
  that degree predictions with grades enabled have
  [a lot of missing data](/documentation/degree_recommendation.md#limitations).
- ATAR data is only provided for courses with enough data and that don't rely on
  other factors like portfolios.
