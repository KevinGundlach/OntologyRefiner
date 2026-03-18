from google import genai 
from google.genai import types
from google.genai.types import File 
from typing import List
import os
from datetime import datetime 

# API_KEY = os.environ.get('DEFAULT_GEMINI_API_KEY')

API_KEY = os.environ.get('ONTOLOGY_REFINER_GEMINI_API_KEY')

def make_client():
    return genai.Client(api_key=API_KEY)

def next_usage_id():

    files = os.listdir("usage")
    ids = [int(f.replace('.txt', '')) for f in files]
    
    if len(ids) == 0:
        return 1
    else:
        return max(ids) + 1

def generate_content(
        client:genai.Client, 
        prompt:str, 
        file:File|None=None, 
        response_json_schema:str|None=None, 
        usage_notes:str|None=None, 
        use_pro:bool=False):

    if file is None:
        contents = [prompt]        
    else:
        contents = [file, prompt]

    if use_pro:
        model = "gemini-3.1-pro-preview"
    else:
        model = "gemini-3-flash-preview"

    thinking_config = types.ThinkingConfig(thinking_level="high")
    
    if response_json_schema is not None:
        content_config = types.GenerateContentConfig(
            thinking_config=thinking_config,
            response_json_schema=response_json_schema,
            response_mime_type="application/json"
        )
    else:
        content_config = types.GenerateContentConfig(
            thinking_config=thinking_config,
            response_mime_type="text/plain"
        )

    response = client.models.generate_content(
        model=model,
        contents=contents,
        config=content_config
    )

    with open(f"usage/{next_usage_id()}.txt", "w") as f:        
        f.write(f"{datetime.now()}\n")
        f.write(f"Notes: {usage_notes}\n")
        f.write(response.usage_metadata.model_dump_json(indent=1))
        
    return response.text
