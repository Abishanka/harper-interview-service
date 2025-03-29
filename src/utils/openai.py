import openai
import os
from openai import OpenAI

from dotenv import load_dotenv

load_dotenv()

# Initialize OpenAI client
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

def openai_completions(prompt, model="gpt-3.5-turbo", response_format=None):
    """
    Call the OpenAI API to generate a completion for a given prompt.
    
    Args:
        prompt: The prompt to send to the OpenAI API.
        model: The model to use for the completion.
        response_format: Optional format specification for structured output.
    
    Returns:
        The generated completion.
    """
    messages = [{"role": "user", "content": prompt}]
    
    kwargs = {
        "model": model,
        "messages": messages,
    }
    
    if response_format:
        kwargs["response_format"] = response_format
    
    response = client.chat.completions.create(**kwargs)
    
    if response_format and response_format.get("type") == "json_object":
        return response.choices[0].message.content
    else:
        return response.choices[0].message.content.strip()