from utils.openai import openai_completions
from utils.anvil import FORM_125_FIELDS
import base64
import json
import httpx
from httpx import ReadTimeout
import os
from dotenv import load_dotenv

load_dotenv()

from prompts import fill_form_fields_prompt, validate_generated_fields_prompt


async def generate_form_background(company_id: str):
    """
        Background task to generate form and print results.
        Generates a PDF and sends it to the frontend service.
    """
    company_data = await fetch_company_data(company_id)

    if "error" in company_data:
        print(f"Error: {company_data}")
        return

    company_md = company_data.get("company", {}).get("md", "")

    filtered_fields = [{
        k: v
        for k, v in field.items() if k != "rect"
    } for field in FORM_125_FIELDS]

    total_batches = (len(filtered_fields) + 24) // 25
    all_results = {}

    for batch_number in range(1, total_batches + 1):
        start_index = (batch_number - 1) * 25
        end_index = min(start_index + 25, len(filtered_fields))
        batch_fields = filtered_fields[start_index:end_index]

        batch_results = await process_field_batch(company_md, batch_fields,
                                                  batch_number, total_batches)
        all_results.update(batch_results)

    all_results = await validate_generated_fields(company_md, all_results,
                                                  FORM_125_FIELDS)

    output_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), '..', 'output'))
    os.makedirs(output_dir, exist_ok=True)
    file_path = os.path.join(output_dir, f"{company_id}.json")
    with open(file_path, "w") as json_file:
        json.dump(all_results, json_file, indent=2)
    print(f"Results saved to {company_id}.json")

    await generate_form(company_id, all_results)


async def generate_form(company_id: str, all_results: dict):
    anvil_api_key = os.getenv('ANVIL_API_KEY')
    if not anvil_api_key:
        print("Error: ANVIL_API_KEY environment variable not set")
        return

    payload = {
        "title": "Acord 125",
        "fontSize": 10,
        "textColor": "#333333",
        "data": all_results
    }

    async with httpx.AsyncClient() as client:
        try:
            pdf_id = company_id.replace(
                "/", "_") if "/" in company_id else company_id
            filename = f"acord125_{pdf_id}.pdf"

            response = await client.post(
                "https://app.useanvil.com/api/v1/fill/GTwwfroD7XjoCtayIlcR.pdf",
                json=payload,
                auth=(anvil_api_key, ""),
                headers={"Content-Type": "application/json"})
            response.raise_for_status()

            output_dir = os.path.abspath(
                os.path.join(os.path.dirname(__file__), '..', 'output'))
            os.makedirs(output_dir, exist_ok=True)
            file_path = os.path.join(output_dir, filename)
            with open(file_path, "wb") as f:
                f.write(response.content)

            print(f"PDF successfully generated and saved as {filename}")

            async with httpx.AsyncClient() as client:
                output_dir = os.path.abspath(
                    os.path.join(os.path.dirname(__file__), '..', 'output'))
                os.makedirs(output_dir, exist_ok=True)
                file_path = os.path.join(output_dir, filename)
                with open(file_path, "rb") as pdf_file:
                    pdf_blob = pdf_file.read()
                    pdf_blob_base64 = base64.b64encode(pdf_blob).decode(
                        'utf-8')
                    response = await client.post(
                        f'{os.getenv("FRONTEND_URL")}/api/generate-pdf',
                        json={
                            "companyId": company_id,
                            "pdfBlob": pdf_blob_base64
                        })
                    response.raise_for_status()
                    print("PDF sent to localhost API successfully.")

        except Exception as e:
            print(f"Error calling Anvil API: {str(e)}")


async def process_field_batch(company_md: str, fields: list, batch_number: int,
                              total_batches: int) -> dict:
    """Process a batch of form fields and return their values."""
    prompt = fill_form_fields_prompt(company_md, fields)

    try:
        response = openai_completions(prompt=prompt,
                                      model="gpt-4o-mini-2024-07-18",
                                      response_format={"type": "json_object"})
        return json.loads(response)
    except Exception as e:
        return {"error": f"Error processing batch {batch_number}: {str(e)}"}


async def validate_generated_fields(company_md: str, generated_fields: dict,
                                    fields: list):
    prompt = validate_generated_fields_prompt(company_md, generated_fields,
                                              fields)
    response = openai_completions(prompt=prompt,
                                  model="gpt-4o-mini-2024-07-18",
                                  response_format={"type": "json_object"})
    return json.loads(response)


async def fetch_company_data(company_id: str):
    """Fetch company data from Retool"""
    url = "https://tatch.retool.com/url/company-memory"
    headers = {
        'Content-Type': 'application/json',
        'X-Workflow-Api-Key': os.getenv('X-Workflow-Api-Key-COMP-MEMORY')
    }
    payload = {"company_id": company_id}

    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
        except ReadTimeout:
            return {"error": "Request timed out. Please try again later."}
        except httpx.HTTPStatusError as exc:
            return {"error": str(exc)}

    return response.json()
