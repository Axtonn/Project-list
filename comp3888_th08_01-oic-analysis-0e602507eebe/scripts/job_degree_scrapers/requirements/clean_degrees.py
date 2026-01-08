"""
Cleans the `job_listing_raw` and `job_degree_requirements_raw`
tables into `careers` and `degree_requirements` tables respectively.
"""
from typing import List, Dict, Callable
import spacy
from spacy.matcher import Matcher, PhraseMatcher
from spacy.tokens import Doc, Span
from scripts.common.db_writer import DbWriter
from scripts.common.element_matcher import last_index
from scripts.job_degree_scrapers.requirements.database_helpers import (
    get_all_degrees, get_degree_requirements, add_degree_requirement,
    create_degree_requirements_table, career_id_from_raw_req)


def lemmatize_lower_span(span: Span) -> str:
    """
    Using a Spacy span, returns the lowercase version of the text with each
    word as a lemma.

    Args:
        span (Span): a span to lemmatize

    Returns:
        str: a lowercase, lemmatized version of the input span
    """
    return " ".join([tok.lemma_ for tok in span]).lower()


def counts_to_frequency(d: Dict[any, int]) -> dict[any, float]:
    """
    Calculate the relative frequency of a key in a dictionary based on its
    number of occurences.

    Args:
        d (Dict[any, int]): A dictionary where the values represent the number
                            of occurrences of a particular key.

    Returns:
        dict[any, float]: A dictionary where the values represent the relative
                          frequency (at most 1) of the keys.
    """
    total = sum(d.values())
    return {key: val / total for key, val in d.items()}


def handle_match(keywords: Dict[str, int], expected_id: str,
                 first: int, last: int) -> Callable:
    """
    Curried handler function for accepting matches from spaCy natural language
    processing. It extracts a desired slice of a matching string and adds the
    slice as lowercase string of corresponding lemmas to the `keywords` dict.

    Args:
        keywords (Dict[str, int]): The dict of matching keywords to add the new
                                   match into
        expected_id (str): The ID of the match as a string
        first (int): The starting position of the desired slice in the original
                     accepting pattern. For instance, in a pattern like 
                     [{'ORTH': "("}, {'ORTH': "example"}, {'ORTH': ")"}], the
                     string, "example", has an index of 1.
        last (int): The end position of the desired slice in the original
                    accepting pattern. For instance, in a pattern like 
                    [{'ORTH': "("}, {'ORTH': "example"}, {'ORTH': ")"}], the
                    string, ")", has an index of 2.

    Returns:
        Callable: A curried function to feed to the `on_match` parameter of
                  `Matcher.add(..., on_match=[this callable])`
    """
    def extract_requirement(_matcher, doc, _id, matches):
        for match_id, start, _end, alignments in matches:
            if not doc.vocab.strings[expected_id] == match_id:
                continue
            match = doc[
                start + alignments.index(first):
                start + last_index(alignments, last) + 1]

            match_lemma = lemmatize_lower_span(match)
            if match_lemma in keywords:
                keywords[match_lemma] += 1
            else:
                keywords[match_lemma] = 1
    return extract_requirement


def get_degree_keywords(degrees: List[str]) -> List[Doc]:
    """
    Extracts keywords for each degree in the provided list.

    Args:
        degrees (List[str]): List of degree names from which to extract keywords.

    Returns:
        List[Doc]: A list of keywords representing the degrees in the given list.
    """
    print("Extracting keywords for associated degrees")
    nlp = spacy.load("en_core_web_trf")
    keyword_match = Matcher(nlp.vocab)

    degree_start_tokens = ["bachelor", "master",
                           "certificate", "doctor", "diploma"]
    degree_pattern = [
        [{'LOWER': {"FUZZY": {'IN': degree_start_tokens}}},
         {'LOWER': {'IN': ["of", "in"]}},
         {'POS': {'IN': ["NOUN", "PROPN"]}, 'OP': '+'},
         ],
    ]
    specialisation_pattern = [
        [{'ORTH': "("},
         {'POS': {'IN': ["NOUN", "PROPN"]}, 'OP': '+'},
         {'ORTH': ")"},
         ],
    ]
    specialisation_conj_pattern = [
        [{'ORTH': "("},
         {'POS': {'IN': ["NOUN", "PROPN"]}, 'OP': '+'},
         {'POS': "CCONJ"},
         {'POS': {'IN': ["NOUN", "PROPN"]}, 'OP': '+'},
         {'ORTH': ")"},
         ],
    ]

    matches = {}
    keyword_match.add("Degree", degree_pattern, greedy="LONGEST",
                      on_match=handle_match(matches, "Degree", 2, 2))
    keyword_match.add("Specialty",
                      specialisation_pattern, greedy="LONGEST",
                      on_match=handle_match(matches, "Specialty", 1, 1))
    keyword_match.add("SpecialtyConj",
                      specialisation_conj_pattern, greedy="LONGEST",
                      on_match=handle_match(matches, "SpecialtyConj", 1, 3))
    for doc in nlp.pipe(degrees):
        keyword_match(doc, with_alignments=True)

    return counts_to_frequency(matches)


def categorise_degree_requirements(
        db_writer: DbWriter, foe: str, degree_keywords: Dict[str, int],
        degree_requirements: List[tuple]) -> List[tuple]:
    """
    Finds all degree requirements that are associated with the given FOE
    based on the degree_keywords of that FOE.

    Args:
        foe (str): The associated FOE
        degree_keywords (Dict[str, int]): _description_
        degree_requirements (List[tuple]): _description_

    Returns:
        List[tuple]: A list of tuple containing the (foe, original row ID of
                     the degree, the text of the best match, the confidence of
                     the best match)
    """
    nlp = spacy.load("en_core_web_trf")
    print("Constructing pattern for matching")

    reqs = [(req[1], {"raw_id": req[0]}) for req in degree_requirements]
    patterns = [nlp(keyword) for keyword in degree_keywords]
    matcher = PhraseMatcher(nlp.vocab, attr="LEMMA")
    matcher.add("degrees", patterns)

    cleaned_requirements = []
    print("Identifying matching rows...")
    for doc, context in nlp.pipe(reqs, as_tuples=True):
        best_match = None
        for _match_id, start, end in matcher(doc):
            match = lemmatize_lower_span(doc[start:end])
            if match not in degree_keywords:
                continue

            if not best_match:
                best_match = match
                continue

            if degree_keywords[match] >= degree_keywords[best_match]:
                best_match = match

        career_id = career_id_from_raw_req(db_writer.con, context["raw_id"])
        if best_match is not None and career_id is not None:
            cleaned_requirements.append(
                (foe, context["raw_id"], best_match,
                 degree_keywords[best_match], career_id[0]))
    return cleaned_requirements


if __name__ == '__main__':
    database_writer = DbWriter()
    create_degree_requirements_table(database_writer.con)
    foe_degrees = get_all_degrees(database_writer.con)
    for code, degree_reqs in foe_degrees.items():
        print(f"---- Cleaning for FOE={code} ---")
        keys = get_degree_keywords(degree_reqs)
        requirement_rows = categorise_degree_requirements(
            database_writer, code, keys,
            get_degree_requirements(database_writer))
        add_degree_requirement(database_writer.con, requirement_rows)
