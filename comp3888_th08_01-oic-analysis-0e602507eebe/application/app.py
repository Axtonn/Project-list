"""This file is used to run the applcation. It handles the gradio server and UI. """

import gradio as gr
from application.career_rec.map_careers import map_careers
import application.reading_user_json as ruj
from application.display_degrees import (
    show_degrees_with_filters, update_student_details)
from application.career_rec.display_careers import show_career_recommendations
from application.functionalities import (
    fetch_foe_data, fetch_foe_detailed_data, generate_combined_output)


if __name__ == "__main__":
    with gr.Blocks() as demo:
        input_json = gr.State({})
        input_json_path = gr.File(file_count="single", file_types=["json"])

        foe_options = fetch_foe_data()
        additional_foe = gr.Dropdown(
            choices=foe_options, label="Select Additional Narrow Field of Education(s)", multiselect=True)

        foe_detailed_options = fetch_foe_detailed_data()
        additional_foe_detailed = gr.Dropdown(
            choices=foe_detailed_options, label="Select Additional Detailed Field of Education(s)", multiselect=True)

        student_details = gr.State(None)
        fields_of_education = gr.Textbox(label="Fields of Education",
                                         placeholder="Your recommended fields of education will be displayed here once your file is uploaded")
        input_json_path.upload(
            ruj.read_json, inputs=input_json_path, outputs=input_json)
        input_json_path.clear(lambda: {}, outputs=input_json)

        input_json.change(update_student_details,
                          inputs=input_json,
                          outputs=student_details)
        input_json.change(ruj.display_foe_names,
                          inputs=[input_json, additional_foe,
                                  additional_foe_detailed],
                          outputs=fields_of_education)
        additional_foe.change(ruj.display_foe_names,
                              inputs=[input_json, additional_foe,
                                      additional_foe_detailed],
                              outputs=fields_of_education)
        additional_foe_detailed.change(ruj.display_foe_names,
                                       inputs=[input_json, additional_foe,
                                               additional_foe_detailed],
                                       outputs=fields_of_education)

        with gr.Tab("Show Recommended Degrees"):
            budget = gr.Slider(minimum=0, maximum=700,
                               step=1, label="Budget (Total Course Cost) in thousands", value=700)

            top_ranked_au_uni = gr.Radio(
                [('Top 3', 3), ('Top 5', 5), ('Top 7', 7),
                 ('Show all Universities', None)],
                label="Top # Ranked Universities in Australia (UOM, USYD, UNSW, etc.)")
            show_degrees_with_filters(
                input_json, budget, top_ranked_au_uni,
                additional_foe, additional_foe_detailed, student_details)

        with gr.Tab("Show Recommended Careers"):
            should_prioritise_uncommon = gr.Radio(
                [("Yes", True), ("No", False)], value=False,
                label="Show me careers I may not have considered?")
            randomness = gr.Slider(
                minimum=0,
                maximum=1,
                value=0,
                step=0.1,
                label="Randomness of results",
                info="0 means not random at all, and 1 means highly random")
            show_career_recommendations(
                input_json, should_prioritise_uncommon,
                randomness, additional_foe, additional_foe_detailed)

        with gr.Tab("Add Career Mappings"):
            map_careers()

        # Section to export results into downloadable JSON.
        with gr.Row():
            update_output_json_button = gr.Button("Update Output JSON")

            download_output_json = gr.DownloadButton(
                label="Download Output JSON")
        with gr.Accordion(label="Show Output JSON", open=False):
            show_output_json = gr.JSON(
                label="Output JSON", show_indices=False, open=True)

        update_output_json_button.click(
            generate_combined_output,
            inputs=[input_json, additional_foe, additional_foe_detailed,
                    budget, student_details, top_ranked_au_uni,
                    should_prioritise_uncommon, randomness],
            outputs=[show_output_json, download_output_json])

    demo.launch(auth=("admin", "Careers!4All"))
