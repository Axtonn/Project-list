# Career Data Cleaning

In order to clean raw data into a useful format for the recommender, we
implemented several cleaning scripts.

## Job and Education Cleaning

Technical details on the cleaning can be found in
[`scripts/job_degree_scrapers/database_cleaning.md`](/scripts/job_degree_scrapers/database_cleaning.md).

Overall, the approach taken in cleaning the data scraped from Indeed and
Workforce Australia (as described in
[`documentation/web_scraping`](/documentation/web_scraping.md)) was to employ
Natural Language Processing (NLP) and Large-Language Models (LLM). Cleaning work
was undertaken in two stages:

1. Cleaning up the job titles
2. Relating education requirements to degrees in our courses table

### Cleaning Up Job Titles

The method we decided to use here was to use an LLM to take the job titles from
the `job_listing_raw` table and condense them into a smaller set of careers. The
~900 listings in the table were reduced to around 400.

Due to the high variance in job titles on the various websites, there would be
several entries for single type of role, like "Tutor". We used OpenAI's API to
merge rows of similar jobs. For instance, the jobs "Data Analyst / Telescope
Operator - SKA-Low Telescope", "Data Analyst", "Data Analyst - GeoServices",
"Data Analyst, Visa Managed Services, Sydney (12-month Fixed Term Contract)",
and "Escalation Response Data Analyst - USDS" were all merged into a single
career—Data Analyst.

This solution leverages the strengths of LLMs. They perform well at parsing
text, generalising information, and are built on large amounts of human-produced
data. This minimizes developer input and isolates biases to that of the LLM.
This solution was also the fastest to develop.

#### Limitations

However, the downsides of this solution are that

- LLMs are difficult to validate and test.
- The output is non-deterministic.
- The output is often too general.
- The cost of this method increases as the data that we produce increases as
  OpenAI's API is not free to use.

The first two issues are somewhat mitigated by manual testing. The third can
also be addressed by doing secondary cleans on the database. In the current
stage of the project, though, these limitations should be noted and considered.

#### Alternate Solutions

- **Use NLP to extract keywords as career names.** This solution would produce
  more reproducible and easily tested results. In order to achieve this though,
  greater attention to the specific format and attributes of the dataset is
  required. While this was feasible for the dataset we collected (just under
  1000 rows of data), it would be much less extensible. As such, this alternate
  solution was not chosen.
- **Use career names from other sources and match scraped data to those names.**
  This method would leverage existing sources like ABS data that is pre-cleaned
  as a "source of truth". The benefits of this are that this would ensure higher
  quality career names and an easier way to connect the two databases in the
  future. One downside is that it would still require NLP or LLMs to execute
  this solution. Additionally, this flow is significantly less parallelisable
  from a timeline standpoint. In order to deliver on the rest of the project, we
  opted not risk delays between preparing the ABS data, and so on. In a more
  ideal world (with less time-crunch), this would likely have been the preferred
  solution.

#### Future Work

The careers in the database can be further merged for better predictions
(currently, many of the careers are either too specific or have titles are that
too vague).

We have found some success in combining careers by matching keywords extracted
through NLP. We found difficulties in merging career titles that are
semantically similar but expressed in different ways. For instance, if there are
two careers called "Aquaculture Farmhand" and "Marine Agriculture Specialist",
then we have not found a reliable method of merging two even as they represent
essentially the same job. It may be useful to consult a data scientist or expert
in NLPs to aid in this design.

In addition, it would be useful to decide what level of specificity is desired
for the career titles. For instance, should "HR Director" be considered
meaningfully different from "HR Manager", or is the more general "HR"
sufficient?

### Relating Education Requirements to Degrees

See
[`Matched Weights` in Career Recommendation](/documentation/career_recommendation.md#matched-weights)

## Linking Job Growth and Careers

Due to the fact that we retrieved data on job growth from a different source
than careers, the way that they title the careers is different. This section
outlines how we linked up the data.

### Rundown

The module uses NLP techniques combined with fuzzy string matching (fuzzywuzzy
lib) to compare and merge job titles of Careers table and Growth_data table

Firstly text preprocessing was implemented by removing stopwords using the
nltk.corpus.stopwords library. This module contains all the stopwords that are
used. This removal helps us focus on the essential content words and improves
matching accuracy by ignoring common stopwords like 'and', 'the', 'or' and more.

Moving onto the second step we used String Matching with the library fuzzywuzzy
which contains the function fuzz.ratio() that can be used to compute a
similarity score between the cleaned job titles. This allows the comparison of
titles with slight variations and allows for the merging of similar job titles
based on a defined threshold (used 90% similarity threshold).

Finally we merge and update the data in the database. The job titles with
similarity score >= 90 are merged into careers table. If no match found, then
job added to careers table and degree requirements table are also updated
accordingly, adding the new job titles in careers into that table.

### Strengths and Limitations

Strengths

1. Effective for dealing with minor variations in job titles such as
   abbreviations, capitalization and reordering of words
2. Requires minimal setup
3. Easily modified using a threshold value, giving us control over matching
   similarity

Limitations

1. Not suited for large-scale datasets. As number of job titles grow, the
   process becomes expensive and time consuming
2. Fuzzy string matching might struggle to differentiate between job titles that
   are contextually different but textually similar (we tried to minimize this
   by upping the threshold)
3. Stopwords may reduce accuracy if there are important for distinguishing
   between some roles

### Alternatives and why they weren't chosen

1. Considered NER (Named Entity Recognition): which can be used to extract
   entities like job titles from text. This wasnt chosen as its very complex to
   setup and it requires a pretrained model for entity extraction which cant be
   done with our time constraint.

2. Word embeddings: compare job titles based on meaning rather than character
   similarity. It has a higher computational complexity and requires more time
   setting up, also more demanding when it comes to traninig data and resources
   to generate embeddings accurately. This approach is suitable for the future
   as it gives more accurate and context-aware matching with the increasing job
   titles.

### NOTES FOR MAGGIE

1. The matching threshold is customizable under the function fuzzy_match_jobs.
   It allows for different degress of strictness depending on project's needs,
   but its good to know that choosing the optimal threshold may require tuning
   based on data characteristics
2. There might be some cases where some jobs may require additional manual
   review and processing as fuzzy matching does not fully capture job titles
   with identical characters but different meanings, such as analyst and data
   analyst or so on.
3. As dataset grows and theres more job titles, it would be wise to consider
   exploring a more advanced NLP technique such as Word embedding or even NER as
   shown above. This ensures better performance and more accurate matching for
   larger datasets where context matters more than character similarity.
