from utils.openai import openai_completions

def get_field_description(field_name, field_type, field_value, options_values):
    prompt = f"Generate a short descriptive description for the field '{field_name}' of type '{field_type}' with the value '{field_value}'."
    if options_values:
        prompt += f" The field has the following options: {options_values}."
    return openai_completions(prompt)

def augment_fields(fields, sample_form):
    for field in fields:
        field_id = field.get("id")
        field_name = field.get("name")
        field_type = field.get("type")
        
        field_value = sample_form.get(field_id, "")

        options = field.get("options", None)
        options_values = []
        if options:
            # Assuming options is a list of dictionaries with 'key' and 'value'
            options_values = [option.get("value") for option in options if "value" in option]
        else:
            options_values = None

        description = get_field_description(str(field_name), str(field_type), str(field_value), str(options_values))

        field.append({
            "augmented_description": description
        })

    return fields
