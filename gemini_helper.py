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

def generate_content(
        client:genai.Client, 
        prompt:str, 
        file:File|None=None, 
        use_pro:bool=False,
        output_json:bool=False):

    if file is None:
        contents = [prompt]        
    else:
        contents = [file, prompt]

    if use_pro:
        model = "gemini-3.1-pro-preview"
    else:
        model = "gemini-3-flash-preview"

    thinking_config = types.ThinkingConfig(thinking_level="high")
    response_mime_type = "application/json" if output_json else None

    generate_content_config = types.GenerateContentConfig(
        thinking_config=thinking_config,
        response_mime_type=response_mime_type
    )
    
    response = client.models.generate_content(
        model=model,
        contents=contents,
        config=generate_content_config
    )

    return response.text
