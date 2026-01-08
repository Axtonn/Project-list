# Official Data

## CRICOS Courses

We are using a publicly recorded list of
[CRICOS approved courses](https://data.gov.au/data/dataset/cricos/resource/67e3b6ac-90de-4a14-bd03-ec021a7b0645?view_id=af05dcb6-0aae-475d-a161-98135633b97b)
as a basic set of degree recommendations. CRICOS courses are available to
domestic and international students. Although this is not as comprehensive a
list as TEQSA courses, it is suitable enough for a product intended for domestic
and international markets. That said, future iterations can investigate ways to
add TEQSA courses to this database as well.

### Limitations

While the FOEs have a logical connection to courses, there are some drawbacks to
relying on FOEs as the primary way input for recommending degrees and careers.

- FOE links in the data sources are self-reported, meaning that similar degrees
  from different reporting unis can have vastly different FOEs.
- This data source links the courses with associated primary, secondary, and
  tertiary FOEs. However, this may not be enough to accurately represent the
  extent to which some courses are related to certain FOEs. For example, a
  bachelors in Materials Engineering is linked to various engineering FOEs in
  the database. However, despite this field's extremely close ties with physics
  and chemistry, this link is not recorded because of the indirect nature of
  those ties. We recommend exploring the following options:
  - Semantic keyword extraction on degree outlines for words relating to other
    FOEs
  - Asking large sample sizes of people to weight the relatedness of FOEs with
    different degree keywords, and aggregating those connections.
  - Consulting faculty coordinators within universities for lists of related
    degrees.
  - Analyzing prohibitions (units that cannot be taken if a student has already
    taken a similar one) under different degrees, and using those links to
    identify degrees that are similar.

## Fields of Education

The
[Australian Standard Classification of Education](https://www.abs.gov.au/statistics/classifications/australian-standard-classification-education-asced/2001#data-downloads)
is supplied by the Australian Bureau of Statistics (ABS) in the form of an XLSX
file which contains was 2 types of Education Classifications:

- Level of Education classification and,
- Fields of Education classification.

Narrow and Detailed Fields of Education were extracted from this file and used
in our system. It was last modified in 29/09/2015, and thus making it a reliable
source.

### Limitations in Using FOEs

Fields of education can have tight links to many careers and degrees. But, for
some, like banking, even the detailed FOEs are too broad, so we are less able to
personalise pathways that are available.

Further, using FOE as the input may be less effective in terms of career
planning than other models. FOEs are a government reporting device for tertiary
education. They are designed to specifically categorise education, not careers.

Models like the

- [Australian and New Zealand Standard Classification of Occupations (ANZSCO)](https://www.abs.gov.au/statistics/classifications/anzsco-australian-and-new-zealand-standard-classification-occupations/2021/classification-structure):
  hierarchical classification of careers into a small number of overarching
  areas by skill level and specialisation
- [Australian Skills Classification](https://www.jobsandskills.gov.au/australian-skills-classification?page=skills):
  Collections of skills that are required for various professions. Directly ties
  into ANZSCO
- [International Classification of Occupations](https://ilostat.ilo.org/methods/concepts-and-definitions/classification-occupation/):
  Hierarchically groups occupations, similar to the ANZSCO, but with slightly
  more focus on skill specialisation than level.

could be more suited for recommending careers without over-reliance on a
student's interest in a subject. Additionally, a more occupation-oriented model
may reduce bias in career recommendations against occupations that are not
directly linked to a specific tertiary degree. For example, venture capitalism
is suited for people who enjoy high-level, client-focused, and fast pace work.
People who go into it can be drawn to study in anything from Computer Science to
Law. Yet, under the FOE model, it would be very difficult to recommend for most
students because it does not have clear links to most fields of study except
business management.

To mitigate these limitations, we paid attention to **algorithmically
highlighting unique career options** to broaden students’ and parents’ horizon -
helping them to consider opportunities they may not have otherwise considered.

## Job Growth and Skill Priority List

The
[Australian Jobs and Skills](https://www.jobsandskills.gov.au/data/occupation-shortages-analysis/occupation-shortage-list?level=4)
data is supplied by most recent data from the Australia Beurau of Statistics
(ABS) and gives indicators of occupation shrotages

- Generalised occupational shortages by state and overall.

This source is considered primary for the usecase. It was last accessed 27/09/24
and it is a credible resource (ABS) of primary data. Some limitations of the
data is considerable dead time in updating of data (annually) and its reliance
of self reporting through census data on occupations. Alternate resources were
considered however limitations assocated were even more exaggerated then via
credible sources.

## Job Growth Projection

The
[Australian Jobs and Skills](https://www.jobsandskills.gov.au/data/employment-projections)
is a projection estimation using a model developed by the University of
Vicotoria and highlights numerical estimation of occupational growth in 2028
and 2033.

- Numerical percentage growth projections expected in occupations.

This source is considered primary for the usecase. It was last accessed 27/09/24
and it is a credible resource (ABS) of primary data. Some limitations of the
data is considerable dead time in updating of data and model based on real time
changes and its reliance of self reporting through census data on occupations
via the ABS. Alternate resources were considered however no well documented
growth model was found within the literature review that had a valid
methodology.

## Job Satisfaction and Job Salaries

The
[SEEK Career Advice](https://www.seek.com.au/career-advice)
pages provide an easy-to-access but detailed overview of job-related factors
of each occupation. Data collected include: job field, job title, typical salary,
satiscation based on reviews, review numbers, job growth prediction, number of
job opportunities in Australia.
Unique points to note include:

- Highly reliable data coming from one of the biggest job boards, SEEK.
  Data from job listings and peoples' profile are used to derive numbers
- To elaborate, columns including salary and job listing numbers are calculated
  based on average annual full time and annualised hourly salaries
  (excluding contract foles) for job ads on SEEK from Apr24 - Jun 24.
- Detailed job satisfaction reviews from people working in the industry.
  Helpful source as this page is rare that it has job review and satisfcation
  classified based on occupation and job field.

Specifically, the data was scraped using the 'Browse Careers by Industry'
section of the website.

### Limitations

Most of the limitations of the dataset came from the usage context of this
dataset within the project. Instead of deriving career-related information
fully from this dataset, it was used linked to the 'careers' dataset, which
was another dataset that was scraped by the team.
The job titles did not achieve a 1-on-1 match, so we had to come up with an
effective method of linking the 2 tables together and extracting relevant
information. We chose to use the 'spacy' module in python and analyze the
similarities between job titles, and link each entry to the entry on the other
table that showed hightest similarity. This way, we could partially justify
the usage of job satisfaction and salary data on jobs with similar job titles.

Another limitation is that the salary data is closer to a representation of
the entire industry of a certain job, rather than a graduate salary data
representation. One suggestion for supplementary data would be the
[QILT Graduate Outcomes Survey](https://qilt.edu.au/surveys/graduate-outcomes-survey-(gos)).
This survey is a self-report survey answered by graduates, about their experience
after graduating university. This data would help support forming another
salary recommendation, which is more heavily weighted on graduate salaries.