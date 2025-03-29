from prompts import identify_fields_to_refine_prompt, update_fields_prompt
from utils.openai import openai_completions
import json
import os

from generate_form import generate_form


async def refine_form_background(company_id: str, refine_task: str):
    output_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), '..', 'output'))
    os.makedirs(output_dir, exist_ok=True)
    file_path = os.path.join(output_dir, f"{company_id}.json")
    with open(file_path, "r") as json_file:
        generated_form = json.load(json_file)
    updated_form = refine_form(refine_task, generated_form)

    await generate_form(company_id, updated_form)


def refine_form(refine_task: str, generated_form: dict):
    fields_of_interest_prompt = identify_fields_to_refine_prompt(
        refine_task, generated_form)
    fields_of_interest = openai_completions(
        prompt=fields_of_interest_prompt,
        model="gpt-4o-mini-2024-07-18",
        response_format={"type": "json_object"})

    updated_form_prompt = update_fields_prompt(refine_task, generated_form,
                                               fields_of_interest)
    updated_form = openai_completions(prompt=updated_form_prompt,
                                      model="gpt-4o-mini-2024-07-18",
                                      response_format={"type": "json_object"})
    return updated_form
