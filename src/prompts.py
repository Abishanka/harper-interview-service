import json
from utils.anvil import ANVIL_FIELDS

def fill_form_fields_prompt(company_md, fields):
    return f"""
### COMPANY & DATA CONTEXT ###

{company_md}

### FIELDS TYPE FORMAT ###
{json.dumps(fields, indent=2)}

### FIELDS TO FILL ###
Generate appropriate values for each field based on the company information. 
Use the following type mappings to format values appropriately:

{json.dumps(ANVIL_FIELDS, indent=2)}

### TASK ###
Generate appropriate values for each field in <FIELDS TO FILL> based on <COMPANY & DATA CONTEXT>.

### RULES ###
1. **Do Not Hallucinate**: Only use data found in the company information provided. If you do not see enough information to fill a field with high confidence, leave it blank.
2. **Strict Format**: Return ONLY a valid JSON object with:
- Keys corresponding to the field IDs in <FIELDS TO FILL>.
- Values formatted according to the type mappings in <FIELDS TYPE FORMAT>.
3. **No Additional Commentary**: Do not include any text outside of the JSON object.

### ANSWER FORMAT ###
Return only the JSON object as your final answer.
"""

def validate_generated_fields_prompt(company_md, generated_fields, fields):
    return f"""
### COMPANY & DATA CONTEXT ###

{company_md}

### GENERATED FORM FIELDS ###
{json.dumps(generated_fields, indent=2)}

### TASK ###
Validate the generated field values against the provided company context. Check for any discrepancies or inconsistencies.

### RULES ###
1. **Strict Format**: Return ONLY a valid JSON object with the same structure as <GENERATED FORM FIELDS>.
2. **Delta**: DO NOT CHANGE THE FIELDS OR STRUCTURE OF THE <GENERATED FORM FIELDS>.
3. **Incorrect Fields**: For each field value that is incorrect, correct the value for that field.
4. **Missing Fields**: For each field value that is missing, add the missing value for that field.
5. **Incorrect Duplicated Values**: Remove any duplicate values for fields that are repeating.
Example:
    - Multiple fields exist for "Applicant Information"
        - Each field is for a UNIQUE applicant
        - Remove applicants that are duplicated
    - Multiple fields exist for "Premises Information"
        - Each field is for a UNIQUE premises
        - Remove premises that are duplicated
6. **No Additional Commentary**: Do not include any text outside of the JSON object.

### ANSWER FORMAT ###
Return only the JSON object as your final answer in the same format as <GENERATED FORM FIELDS>.
"""

def identify_fields_to_refine_prompt(refine_task:str, generated_fields:dict):
    return f"""
### GENERATED FORM FIELDS ###
{json.dumps(generated_fields, indent=2)}

### REFINEMENT QUERY ###
{refine_task}

### TASK ###
There may be multiple fields that need to be updated.
There may be one fields that need to be updated but multiple similar fields exist.
Identify all the fields that may needed to be refined / updated to complete the <REFINEMENT TASK>.

### RULES ###
1. **Strict Format**: Return ONLY a list of valid JSON objects. Each object should EXACTLY MATCH the what is in <GENERATED FORM FIELDS>.
2. **No Additional Commentary**: Do not include any text outside of the JSON object.

### ANSWER FORMAT ###
Return a list of fields, where each field is a JSON object in <GENERATED FORM FIELDS>.
"""

def update_fields_prompt(refine_task:str, generated_fields:dict, fields_of_interest:list):
    return f"""
### GENERATED FORM FIELDS ###
{json.dumps(generated_fields, indent=2)}

### FIELDS OF INTEREST ###
{json.dumps(fields_of_interest, indent=2)}

### REFINEMENT TASK ###
{refine_task}

### TASK ###
Update the fields in <GENERATED FORM FIELDS> that need to be updated to complete the <REFINEMENT TASK>.
All the fields that are changed SHOULD BE in <FIELDS OF INTEREST>.
NOT ALL FIELDS IN <FIELDS OF INTEREST> NEED TO BE CHANGED.

### RULES ###
1. **Strict Format**: Return ONLY a valid JSON object with the same structure as <GENERATED FORM FIELDS>.
2. **Data Type**: Return the values in the same data type as they are in <GENERATED FORM FIELDS>.
3. **No Additional Commentary**: Do not include any text outside of the JSON object.

### ANSWER FORMAT ###
Return only the JSON object as your final answer in the same format as <GENERATED FORM FIELDS>.
"""