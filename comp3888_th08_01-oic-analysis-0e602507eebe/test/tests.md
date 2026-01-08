# Testing

This file documents the automated tests that have been created for this project.
Broadly, there is one category of test that is currently implemented: unit
testing.

## Unit Tests

### Degree Requirements and Cleaning

#### [Element Matcher Tests](/test/unit_tests/test_element_matcher.py)

Located in
[`test/unit_tests/test_element_matcher`](unit_tests/test_element_matcher.py),
this suite tests
[`scripts/common/element_matcher.py`](../scripts/common/element_matcher.py).

The tests are as follows:

##### `find_text` Tests

- `test_find_text_in_top_level_tag`: Positive. Verify that the function can
  locate and return text exactly matching the innerHTML of a top-level tag.
- `test_find_text_in_nested_tag`: Positive. Verify that it can find an element
  that is not top-level with innerHTML exactly matching the provided text.
- `test_find_text_returns_with_partial_match`: Positive. Verify that it can find
  a top level element with a partial match to provided text.
- `test_find_text_returns_first_match`: Edge. Verify it returns the first
  matching element if multiple could be found.
- `test_find_text_returns_partial_with_other_children`: Edge. Verify it returns
  a matching element even if there are other nested tags apart from the
  innerHTML text
- `test_does_not_find_partial_match_in_children`: Negative. Verify it does not
  match elements with the wrong tag, even if they are children.

##### `extract_degree_requirements` Tests

- `test_extract_degree_requirements_matches_bachelors`: Positive. Verify that
  string tags containing "Bachelor of" or "Bachelor in" are matches
- `test_extract_degree_requirements_matches_masters`: Positive. Verify that
  string tags containing "Master of" or "master in" are matches
- `test_extract_degree_requirements_multiple_degrees`: Positive. Verify that
  multiple matches are all returned.
- `test_extract_degree_requirements_degree`: Edge. Verify that tags containing
  both "bachelor of" and "degree" in them are matched
- `test_extract_degree_requirements_no_degree_of`: Negative. Verify that "degree
  of" is not a matched.

#### [Indeed Data Scrape Tests](/test/unit_tests/test_indeed_data_scrape.py)

##### `run_scraper` Tests

- `test_no_jobs_no_pages_found_exits`: Edge. Verify that, if no more "next page"
  buttons are found, the program exits without doing anything
- `test_accesses_job_details`: Positive. Verify that, when jobs are found, there
  is an attempt to access the details of each job. However, if there are no
  details to be found, then no data is written.
- `test_writes_non_empty_requirements`: Positive. Verfify that, if a job has job
  details that are found, then it will be written to the database.

##### `extract_job_details` Tests

- `test_extracts_empty_list`: Negative. If there are no job details to be found
  on a page, then an empty list is returned
- `test_extracts_empty_if_no_requirements`: Edge. Even if is pay and location
  information is present, they will not be returned
- `test_extracts_none_if_location_pay_empty`: Positive, If there is no pay or
  location information, they default to `None`
- `test_extracts_exists_if_location_pay_non_empty`: Positive. Extracts all
  information if available.

##### `last_index` Tests

- `test_last_index_finds_last`: Positive. Returns the index of the last matching
  element.
- `test_last_index_finds_first_if_uniq`: Edge. If there is only one instance of
  a matching element, return the index of that element.
- `test_last_index_raises_error_if_not_exists`: Edge. If the element does not
  exists, it should raise a value error (the same way that `list.index()` raises
  an error).

#### [Database Helpers](/test/unit_tests/test_requirements_database_helpers.py)

- Testing `get_all_degrees`:
  - `test_fetches_degrees_as_dict`: Positive. Ensures that the degrees are
    fetched as a dictionary of values.
  - `test_does_not_fetch_null`: Negative. Ensures that courses without FOE
    connections are not fetched .
  - `test_uses_only_first_letters`: Edge. Test the edge case where several FOEs
    have the same primary FOE, but the FOEs have differing trailing text. Only
    the initial code should be considered .
  - `test_uses_only_distinct_courses`: Edge. When there are several rows with
    the same course name for an FOE, no duplicates are returned.
- Testing `create_degree_requirements_table`:
  - `test_creates_degree_requirements_table_with_right_schema`: Positive. Checks
    that the degree requirements table is instantiated correctly.
  - `test_creates_degree_requirements_table_succeeds_if_exists`: Edge.
    Attempting to create the table when it already exists does not fail.
  - `test_creates_degree_requirements_table_fails_on_operation_error`: Negative.
    Operation Error results in quiet failure.
  - `test_creates_degree_requirements_table_throws_on_exception`: Edge.
    Non-SQLite errors thrown will not be caught.

#### ATAR Scraping Tests

##### [UAC Scraping Tests](/test/unit_tests/test_admissions_uac_parser.py)

- Testing `input_institution_name`
  - `test_inputs_correct_name`: Positive. The search bar has the right value
    inputed
  - `test_input_fails_on_element_not_found`: Negative. Function returns False if
    there is no search bar.
- Testing `get_data_from_tab`
  - `test_get_data_from_tab_all_data`:
  - ``:
- Testing `handle_atar_table`
  - `test_handle_atar_table`: Tests that, given a HTML page with an ATAR table
    displaying minimum, median, and maximum accepted ATARs (adjusted and
    non-adjusted), that data is extracted and returned as a list.
  - `test_handle_atar_table_mult_rows`: Tests that, given a HTML page with an
    ATAR table with multiple rows, the minimum of the minimum accepted ATARs is
    returned, and the median of the medians is returned.
  - `test_handle_atar_table_no_data_in_any`: If there is no data or malformed
    values in any of the cells in a table, then an empty list is returned
  - `test_handle_atar_table_no_data_keep_no_data`: If there is no data for an
    acceptable reason in a cell, than that cell is ignored and `None` is
    returned in its place.
- Testing `write_data`

##### [Admissions Data Function Tests](/test/unit_tests/test_admissions_atar_data_helper.py)

- Testing `check_admission_requirements_exist`
  - `test_admission_internal_code_already_exist_true`: Positive. Function
    returns True if the row exists based on the internal code
  - `test_admission_internal_code_does_not_exist_false`: Negative. Function
    returns false if the entry does not exist based on the internal code
  - `test_admission_cricos_already_exist_true`: Postive. Function returns True
    if the entry exists based on CRICOS number
  - `test_admission_cricos_does_not_exist_false`: Negative. Function returns
    False if the entry does not exist based on CRICOS number
  - `test_admission_errors_does_not_exist`: Edge. Function returns False if
    there is a SQLite error while fetching.
  - `test_admission_false_no_cricos_or_internal_code`: Edge. Autofail if no
    CRICOS or internal code is given.
- Testing `find_matching_course`
  - `test_finds_matching_course_case_insensitive`: Positive: returns a match to
    any course with the same name regardless of case as a list.
  - `test_does_not_find_matching_course`: Negative. Returns an empty list if
    there are no matching entries.
  - `test_does_not_find_matching_course_on_error`: Edge. Returns an empty list
    when there is an error while fetching data.
- Testing `insert_admission_requirement`
  - `test_inserts_single_admissions_row`: Positive. Tests that an entry is
    inserted with the correct details.
  - `test_skips_if_exists`: Edge. Tests that an insertion is skipped without
    failure if a course with the same CRICOS number is inserted.
  - `test_does_insert_on_error`: Edge. IF there is an error while inserting the
    data, then the function returns False and no data is written.

### FOE Script Tests

Located in
[`test/unit_tests/test_foe_script.py`](unit_tests/test_foe_script.py), this
suite tests
[`scripts/foe_script/foe_script.py`](../scripts/foe_script/foe_script.py).

The tests are as follows:

- `test_read_excel_file`: Verify that the function returns the expected
  panda.DataFrame object along with the expected print statement.
- `test_extract_narrow_fields`: Verify that the function correctly takes in a
  panda.DataFrame containing columns ('Narrow Fields', 'Unnamed: 2', etc..) and
  returns a panda.DataFrame that only contains the columns ('Narrow Fields',
  'Unnamed: 2') renamed to 'code' and 'name' respectively.
- `test_output_to_csv`: Verify that the function correctly outputs the
  panda.DataFrame into the CSV path given along with the expected print
  statement.
- `test_create_foe_table`: Verify that the function correctly executes the
  sequel command to create the 'foe' table with the expected print statement,
  and when a sqlite3.OperationalError is raised, the expected print statement is
  shown.
- `test_insert_into_database`: Verify that the function correctly executes the
  sequel command to insert the panda.DataFrame data into the 'foe' table with
  the expected print statement, and when a sqlite3.IntegrityError is raised, the
  expected print statement is shown.

### Datagov Script Tests

Located in
[`test/unit_tests/tests_datagov_script.py`](test/unit_tests/test_datagov_script.py)

The tests are as follows:

- `test_import_csv_to_sqlite`: Verifies that the function correctly imports data
  from a well-formed CSV file into a SQLite table.
- `test_create_courses_table`: Verifies that the courses table is created with
  the correct schema, ensuring it includes all necessary columns like
  institution_id, course_id, course_name, foe1_broad_field, and more.
- `test_create_institutions_table`: nsures that the institutions table is
  created with the correct schema, containing the appropriate column names and
  types (institution_id, institution_name, and institution_type).
- `test_create_course_locations_table`: Verifies that the course_locations table
  is correctly created with the appropriate schema, ensuring columns like cl_id,
  course_id, location_name, city, and state are defined.
- `test_create_locations_table`: Ensures the locations table is created with the
  correct schema, including columns such as l_id, location_name, address_line_1,
  city, state, and postcode.
- `test_table_already_exists`: Checks that the script handles the case where a
  table already exists without causing an error (e.g., attempting to create the
  institutions table twice should not raise an exception).

### Career Recommender Tests

- `test_recommends_5_ordered_careers_for_foe` Test: Positive. Checks that only 5
  careers are returned in the correct format and order (based on total weights)
  under default conditions and with no interference from other FOE listings.
- `test_recommends_none_careers_for_invalid_foe` Test: Negative. Checks that an
  empty list is returned when the foe cannot be found.
- `test_values_rarity_if_selected` Test: Postive. Ensures that, should
  `prioritise_uncommon` be true, then careers that appear in the requirements
  databaes less frequently are boosted.
- `test_recommends_less_than_5_if_none_available`: Edge. Tests that fewer than 5
  results are returned if there are not enough rows.

### Career and Job Growth Merge Tests

- `test_clean_text`: Ensures that the clean_text function properly processes
  text by converting it to lowercase and normalizing spaces.
- `test_load_data`: Verifies that the load_data function correctly loads data
  from the growth_data and careers tables into DataFrames.
- `test_clean_job_titles`: Confirms that the clean_job_titles function generates
  a clean_name column in both the growth_data and careers DataFrames.
- `test_fuzzy_match_jobs`: Checks that the fuzzy_match_jobs function matches
  jobs between growth_data and careers using fuzzy matching and that matches are
  correctly identified.
- `test_merge_and_update`: Tests the merge_and_update function to ensure that
  matched jobs are properly merged into the careers DataFrame and that
  degree_requirements are updated accordingly.
