import gradio as gr

from application.functionalities import fetch_foe_data
from scripts.common.db_writer import DbWriter


def get_manual_recommend_careers():
    """
    Fetches all careers in the requirements table that need a manual entry
    for their FOE codes.

    Returns:
        List: A list of all careers, with the requirement ID, career ID,
            and career title as a tuple.
    """
    template = """
        SELECT r.requirement_id, r.career_id, c.career_name
        FROM careers AS c JOIN degree_requirements AS r
            ON c.career_id = r.career_id
        WHERE r.foe_code = "Manual Entry Needed"
        """

    db = DbWriter()
    with db.con as con:
        cursor = con.cursor()
        cursor.execute(template)

    return cursor.fetchall()


def insert_new_relationships(careers, index, foes, weight):
    """
    Add entries into the requirements table. Entries may be duplicates of
    existing ones.

    Args:
        careers (List[Tuple[int, int, str]]): A list of career IDs and names.
        index (int): The current career between matched
        foes (List): List of applicable `{'code': FoE code, 'name': FOE name}`
        weight (float): How tightly the career matches the foes.

    Returns:
        bool: True on success. False otherwise.
    """
    if foes is None:
        return False
    template = """
        INSERT INTO degree_requirements(foe_code, career_id, matched_weight)
        VALUES(?, ?, ?)
        """

    values = [(foe["code"], careers[index][1], weight)
              for foe in foes]

    db = DbWriter()
    with db.con as con:
        cursor = con.cursor()
        cursor.executemany(template, values)

    delete = """
        DELETE FROM degree_requirements 
        WHERE foe_code = "Manual Entry Needed" AND career_id = ?
    """

    with db.con as con:
        cursor = con.cursor()
        cursor.execute(delete, (careers[index][1],))
    return True


def map_careers():
    career_index = gr.State(0)
    careers_to_update = gr.State(get_manual_recommend_careers())
    success = gr.State(None)

    foe_options = fetch_foe_data()

    gr.Markdown(f"""
                 ## Description

                 Manually fill in mappings between FOEs and careers for
                 {len(careers_to_update.value)} rows of data
                 """)
    with gr.Row():
        foes = gr.Dropdown(
            choices=foe_options, label="FOEs", multiselect=True, scale=2)
        weight = gr.Slider(value=0.5,
                           label="Weight",
                           step=0.005,
                           interactive=True,
                           minimum=0,
                           maximum=0.5,
                           scale=1)

    @gr.render(inputs=[career_index, careers_to_update, foes, weight, success])
    def show_career_fields(i, careers, foes, weight, success):
        gr.Markdown(f"""
                    ## Mapping for {careers[i][2]}
                    Career No. {i}/{len(careers)} (ID#{careers[i][1]})

                    Weight {weight} will be applied to:
                    """)

        if not foes:
            gr.Markdown("``````")
            return
        foes_str = "```\n" + "\n".join([f"{k}: {foe["code"]} - {foe["name"]}"
                                        for k, foe in enumerate(foes)]) + "\n```"

        gr.Markdown(foes_str)

        if success is not None:
            gr.Markdown(f"### Success: {success}")

    with gr.Row():
        prev_career = gr.Button("Prev", interactive=True)
        submit = gr.Button("Update", interactive=True)
        next_career = gr.Button("Next", interactive=True)
        submit.click(insert_new_relationships,
                     inputs=[careers_to_update, career_index, foes, weight], outputs=[success])
        prev_career.click(lambda i, c: (i - 1) % len(c), inputs=[
            career_index, careers_to_update], outputs=[career_index])
        next_career.click(lambda i, c: (i + 1) % len(c), inputs=[
            career_index, careers_to_update], outputs=[career_index])
