from google import genai 
from google.genai import types
from google.genai.types import File 
from typing import List
import os
from datetime import datetime 

API_KEY = os.environ.get('GEMINI_API_KEY')

def make_client():
    return genai.Client(api_key=API_KEY)

def next_usage_id():

    files = os.listdir("usage")
    ids = [int(f.replace('.txt', '')) for f in files]
    
    if len(ids) == 0:
        return 1
    else:
        return max(ids) + 1

def generate_content(client:genai.Client, prompt:str, file:File|None=None, response_mime_type:str|None=None, usage_notes:str|None=None):

    if file is None:
        contents = [prompt]        
    else:
        contents = [file, prompt]

    response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=contents,
        config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_level="high"),
            response_mime_type=response_mime_type,
        ),
    )

    with open(f"usage/{next_usage_id()}.txt", "w") as f:        
        f.write(f"{datetime.now()}\n")
        f.write(f"Notes: {usage_notes}\n")
        f.write(response.usage_metadata.model_dump_json(indent=1))
        
    return response.text
