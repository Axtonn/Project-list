"""
Custom LLM Task to categorises job titles into general career paths.
"""
from typing import Iterable
from spacy.tokens import Doc
from spacy_llm.registry import registry


@registry.llm_tasks("oic_analysis.CategoriseCareers.v1")
def make_career_categorisation() -> "CategoriseCareers":
    return CategoriseCareers()


class CategoriseCareers:
    """
    Custom LLM Task with prompt and parsing.
    """

    def __init__(self):
        self.prompt = """
            ## Data
            job_id, job_title
            {}

            ## Instructions
            As a data cleaning script, extract a list of strings 
            "career_name - job_ids" from the the data section above. The 
            `career_name` should be a string of no more than 3 words that is 
            generalised from the values in the `job_title` column of the data.
            Ensure that all career names are normalised and are general
            occupation fields.

            The `job_ids` should be a comma-separated list of 2 or more
            integers. The `job_ids` should also be a one-to-many map to the 
            `job_id` column for any rows where the `job_title` is generalised 
            to the `career_name`. a `job_id` appears at most once in the list.

            There must be no more than half the number of input lines as output.

            Remove acronyms.

            ## Example
            For example, if the data was
            "1, Video Editor
            2, Social media Video Manager
            3, Clinical Research Associate Entry
            4, UniSA Online Academic Casual Tutor Register
            5, Remote Tutor"

            You can output
            "Videographer / Video Editor - 1,2
            Researcher - 3
            Academic Tutor - 4,5"
            """

    def unpack(self, response: str):
        """
        parse a particular response with the expected format of
        ['"career1 - id,id,id\ncareer2 - id"']
        """
        lines = response[0].strip('"').split("\n")
        return [tuple(line.strip().split(" - ")) for line in lines]

    def generate_prompts(self, docs: Iterable[Doc]) -> Iterable[str]:
        """
        For every input document, create a generator for the GPT prompt.
        """

        prompt_counter = 1
        for doc in docs:
            print("Generating ChatGPT Prompt #" + str(prompt_counter))
            prompt_counter += 1
            yield self.prompt.format(doc.text)

    def parse_responses(
        self, docs: Iterable[Doc], responses: Iterable[str]
    ) -> Iterable[Doc]:
        """
        Create a generator to parse every response to a prompt.
        """

        response_counter = 1
        for doc, response in zip(docs, responses):
            print("Parsing response #" + str(response_counter))
            response_counter += 1
            if not Doc.has_extension("categories"):
                Doc.set_extension("categories", default=None)
            setattr(doc._, "categories", self.unpack(response))
            yield doc
