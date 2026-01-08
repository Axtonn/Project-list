import json
import gradio as gr


def display_foe_names(input_json, additional_foe, additional_foe_detailed):
    """
    Reads input data from a JSON file and
    extracts the names of the narrow fields of education (FOE).

    Args:
        input_json (str): Path to the input JSON file.

    Returns:
        str: A newline-separated string containing the FOE names.
    """

    result = ""
    foe_codes = set()
    if input_json:
        for field in input_json["inputs"]:
            if field["code"] not in foe_codes:
                result += field["code"] + " " + field["name"] + "\n"
                foe_codes.add(field["code"])
    if additional_foe:
        for foe in additional_foe:
            if foe["code"] not in foe_codes:
                result += foe["code"] + " " + foe["name"] + "\n"
    if additional_foe_detailed:
        for foe in additional_foe_detailed:
            if foe["code"] not in foe_codes:
                result += foe["code"] + " " + foe["name"] + "\n"
    return result


def get_student_id(input_json):
    """
    Reads student id a JSON file and outputs the raw id.

    Args:
        input_json (str): Path to the input JSON file.

    Returns:
        int|None: The id of the student in the input file.
    """

    return input_json["student_id"] if "student_id" in input_json else None



def read_json(json_path):
    with open(json_path) as json_file:
        data = json.load(json_file)

    return data
