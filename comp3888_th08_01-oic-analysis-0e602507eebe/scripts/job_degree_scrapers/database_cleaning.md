# Technical Notes on Database Cleaning

The purpose of the `database_cleaning.py` script is to take the raw data
collected by webscraping from Indeed and Workforce Australia and create usable,
clean data. The script creates new tables and maps relationships between those
tables and existing ones.

## Database Schema

The script adds two new tables into the database: `careers` and
`degree_requirements`. These are cleaned versions of `job_listings_raw` and
`job_degree_requirements_raw` respectively

### Careers Table

The `careers` table contains career entries that have been cleaned with genAI
models. Its basic schema is the following:

```sql
CREATE TABLE careers {
  career_id INTEGER PRIMARY KEY,
  career_name TEXT UNIQUE
}
```

Further columns may be added to this table, including salary, satisfaction, and
growth data.

### Degree Requirements Table

The `degree_requirements` table summarises the field of degrees that are
required for particular careers. It represents the relationship between an FOE
(that itself is connected to various courses and degrees) and corresponding
careers.

The schema is as follows

```sql
CREATE TABLE degree_requirements {
  requirement_id INTEGER PRIMARY KEY,
  foe_code TEXT,
  raw_requirement_id INTEGER,
  career_id INTEGER,
  matched_text TEXT,
  matched_weight FLOAT,
  FOREIGN KEY(foe_code) REFERENCES foe(code),
  FOREIGN KEY(raw_requirement_id) REFERENCES
    job_degree_requirements_raw(degree_id),
  FOREIGN KEY(career_id) REFERENCES
    careers(career_id)
}
```

For each particular FOE present in the `foe` table, a list of keywords was
computed (through natural language processing) based on titles of related
courses. Then, every requirement scraped into the `job_degree_requirements_raw`
was compared with the list of keywords to find matches. Those matches were
recorded in this table, with the job titles from each match getting linked to a
cleaned career.

Some detailed explanation for the columns follows:

- `raw_requirement_id`: a reference to the row in `job_degree_requirements_raw`
  that an entry in this table is based on.
- `career_id`: The id of the cleaned entry for a career. We get this from the
  job listing (`job_listing_raw.job_id`) that an entry in
  `job_degree_requirements_raw` is associated with. That job_listing has
  possibly been categorised into a more general career name in `careers`. If it
  has, then that link is established in the new table.
- `matched_text`: The keyword (usually a 1-3 word phrase) that was used to match
  this foe up with a degree_requirement.
- `matched_weight`: The relative likelihood (between 0 and 1) that the entry is
  a good match between foe and career. A high number means that the keyword in
  `matched_text` is strongly associated with the particular FOE (due to having
  many related courses all having similar names)

## Requirements

This script relies on Natural Language Processing (NLP) libraries
[(SpaCy)](https://spacy.io/) and Large Language Models (LLMs) in order to
categorise the job titles and degrees collated from various websites.

The requirement should be installed using
`pip install -r scripts/job_degree_scrapers/degree_clean_requirements.txt`.

However, there are few notable decisions that were made.

### SpaCy Model

The module uses [`en_core_web_trf`](https://spacy.io/models/en#en_core_web_trf)
as the trained NLP pipeline. Different pre-trained pipelines offer varying
amounts of efficiency and accuracy for different languages. The chosen model is
an English model that heavily prioritises accuracy over efficiency.

Given that we have a relatively small amount of data, and this script is
intended to be run only once every few weeks or months, the drop in efficiency
does not greatly impact the performance of the system as a whole. As such,
accuracy is prioritised over efficiency.

In the future, should performance need to be prioritised over accuracy, then it
is recommended to switch the model using
`python -m spacy download <model_name>`. The models that are more efficient are

- [`en_core_web_sm`](https://spacy.io/models/en#en_core_web_sm): Smallest, most
  efficient model.
- [`en_core_web_md`](https://spacy.io/models/en#en_core_web_md): Medium size.
  Less efficient than small, but more efficient than TRF.

### LLM: OpenAI and SpaCy

For consistency, we are using SpaCy's in-built LLM functionality to categorise
careers from job titles. SpaCy can integrate with various different LLMs, but
OpenAI's GPT-4 was chosen instead as a well-documented and efficient model.

To use the script, you must have access to an OpenAI API key. Currently, we are
using personal API keys for the purposes of development. As OIC scales up, this
may need to be replaced with a company key. There is a cost associated with
using OpenAI API keys.

Once the
[API key has been generated](https://platform.openai.com/docs/quickstart/create-and-export-an-api-key),
it should be added to the shell as an environment variable in terminal. The
simplest way to implement this is to

1. Open your device's `~/.zshrc` or `~/.bashrc` configuration file
2. Add the line `export OPENAI_API_KEY="sk-..."`.
3. Run `source ~/.zshrc` or `source ~/.bashrc` as needed.

## Usage

The career cleaning script must be run before the requirements cleaning script:
`python3 -m scripts.job_degree_scrapers.career_cleaner.clean_careers`. You'll
need access to an internet connection.

Then the requirements cleaning script can be run:
`python3 -m scripts.job_degree_scrapers.clean_degrees`
