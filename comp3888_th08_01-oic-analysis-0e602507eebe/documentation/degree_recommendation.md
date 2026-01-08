<!-- vscode-markdown-toc -->

<!-- vscode-markdown-toc-config
	numbering=false
	autoSave=true
	/vscode-markdown-toc-config -->
<!-- /vscode-markdown-toc -->

# Degree Recommendation

- [Degree Recommendation](#markdown-header-degree-recommendation)
  - [Grades](#markdown-header-grades)
    - [Storage](#markdown-header-storage)
    - [Recommendation](#markdown-header-recommendation)
      - [Strengths](#markdown-header-strengths)
      - [Limitations](#markdown-header-limitations)
  - [Budget](#markdown-header-budget)
  - [Uni Rankings](#markdown-header-uni-rankings)

The
[degree recommendation algorithm](https://bitbucket.org/comp3888_th08_01/oic-analysis/src/18015bf267cae23ebe88b6fa9f2a873ce7952de4/application/display_degrees.py#application/display_degrees.py-66)
factors in high school grades, budget, and uni ranking to suggest suitable
degrees for a student.

## Grades

When using the GUI, grades can be optionally added to the recommender algorithm
by uploading a test input file with a `student_id` value.

### Storage

The grades for each student are stored against their student ID. As discussed
with the other P43 team, the input we received from them will only include a
list of FOEs and a student's ID.

In our database, students are tracked in the `students` table, which contains
their

- `student_id`
- `given_name`
- `surname`
- `location`

Currently, the sample data provided by Grace has been pre-filled into the
database, with an additional student, "Jane Doe".

Separately, the `grades` table tracks the the scores that students have achieved
in various `examination_systems`. We separated this from the students table for
extensibility. We anticipate that there may be students who have scores in
multiple different exams (such as both SAT and AP) as OIC Education expands. A
separate table facilitates that one to many relationship much better, even if it
is less ideal for space complexity.

Individual subject scores could also be tracked here, with an appropriate value
in `grade_type`. Information in the `grades` table include

- `student_id`
- `grade_type`
- `score`

The `examination_systems` keeps track of information different exam formats.
This can be extended in the future to also track conversions between exam types.
It currently contains:

- `grade_type` one of ("ATAR", "GAOKAO")
- `max_score`
- `country` the origin or primary location where the exam format is used.

### Recommendation

Student grades are used to identify target and reach courses that they may be
suited for.

**Target courses**: These are courses that the student is likely or guaranteed
to matriculate into, provided that their grades are maintained. Mathematically,
it is calculated as any course with either a guaranteed ATAR or median ATAR
[between 0 and the student’s ATAR + 1](https://bitbucket.org/comp3888_th08_01/oic-analysis/src/18015bf267cae23ebe88b6fa9f2a873ce7952de4/application/display_degrees.py#application/display_degrees.py-97:99).

**Reach courses**: These are courses that the student could possibly achieve
through additional effort. Mathematically, this is any course with either a
[guaranteed or median ATAR](https://bitbucket.org/comp3888_th08_01/oic-analysis/src/18015bf267cae23ebe88b6fa9f2a873ce7952de4/application/display_degrees.py#application/display_degrees.py-106)
that is

- Greater than the student’s ATAR + 1 and
- Less than their
  $\text{grade} + \dfrac{\text{ATAR\_MAX} - \text{grade}}{4}\times \log_{10}(\text{grade})$

The below graph shows what ATARs are considered a viable “reach” goal (black)
for different ATARs (purple). the higher the current ATAR, the harder it is to
improve more.

![Reach vs Target ATAR](/documentation/assets/target_reach_atar.png)

#### Strengths

- Separates achievable and ideal courses.
- The formula considers that it becomes harder to raise an ATAR grade the closer
  a person gets to the maximum grade.

#### Limitations

- Students may want to see all available courses and weigh their options, but
  this limits that ability (We can return a list of all courses in addition
  instead)
- Some courses do not use ATAR for matriculation. Instead they rely on things
  like portfolios. Considering these cases was not in scope, but they do present
  an opportunity for development in the future.
- The reach courses curve is defined heuristically. It is not based on data of
  what actual achievable ATARs are based on a student's current ATAR.
- The link between FOEs is only considered at the primary level (i.e. what FOE
  is considered to be the primary one for a particular degree). This means that
  an FOE like Physics and Astronomy will not return many degrees that are
  clearly related to Physics but are not labelled as such in the databae. This
  could be partially mitigated by incorporating the second and third FOEs. Other
  options include semantic text matching.

## Budget

The budget is implemented as a simple cutoff. Courses with total costs above a
given threshold are not considered. In the GUI, this can be added to the
algorithm by interacting with the "Budget" slider.

This is not tailored to individual families or student ambitions as finances may
change depending on family circumstances, scholarships, and other factors.

## Uni Rankings

Degrees can be filtered for the top 1, 3, 5, or 7 universities in Australia. In
the GUI, this can be added to the algorithm by interacting with the Top Uni
radio buttons.

In an earlier iteration, the rankings would influence the return order of
degrees. However, this was replaced by the current implementation, where the
rankings only determing whether a degree is included or excluded.

Our implementation only uses the overall univeristy ranking. Due to time
constraints, we were not able to include per-discipliine rankings. As a result,
this filter in the algorithm will only provide information that parents and
students are likely to already have easy access to.

Note that, due to limited ATAR data currently, this does not interact well with
the grades yet.
