# README #

This README Shows the reasoning behind the cleaning process and what was removed from the datasets to narrow down the relevant fields for the algorithm

# STEPS #

## STEP 1 ##
- Download the xlsx files 
- Manually remove irrelevant lines that are not part of the dataset
- By then the files should be readable in xlsx

## STEP 2 ##
Manually remove columns that:
- contain way too many missing values
- irrelevant to the algorithm

### COURSES DATASET ###
- Remove Dual qualification
- Remove VET CODE
- Remove FOE2 Broad
- Remove FOE2 Narrow
- Remove FOE2 Detailed
- Remove Foundation studies
- Remove Work component 
- Remove Work Component Hours/Week
- Remove Work Component Weeks
- Remove Work Component Total Hours
- Remove Course language
- Remove lines with Yes in Expired Column
- Remove expired column


### INSTITUTION DATASET ###
- Remove trading name
- Remove institution capacity
- Remove website
- Remove address Line 2
- Remove address Line 3
- Remove address Line 4


### COURSELOCATIONS DATASET ###
- Remove Institution ID
- Remove Institution Name


### LOCATIONS DATASET ###
- Remove InstitutionName
- Remove Location Type
- Remove address Line 2
- Remove address Line 3
- Remove address Line 4


## STEP 3 ##
- Change datatypes accordingly
- Rename columns accordingly

## STEP 4 ## 
- convert to csv 
- import to database