import os
from openai import OpenAI
from typing import Literal
from dataclasses import dataclass

@dataclass 
class ModelSettings:
    model_url : str 
    model_api_key : str 
    model : str 

    @classmethod
    def gemini_flash(cls):
        return ModelSettings(
            model_url = "https://generativelanguage.googleapis.com/v1beta/openai/",
            model_api_key = os.environ.get('ONTOLOGY_REFINER_GEMINI_API_KEY'),
            model = "gemini-3-flash-preview"
        )

    @classmethod
    def gemini_pro(cls):
        return ModelSettings(
            model_url = "https://generativelanguage.googleapis.com/v1beta/openai/",
            model_api_key = os.environ.get('ONTOLOGY_REFINER_GEMINI_API_KEY'),
            model = "gemini-3.1-pro"
        )

    @classmethod 
    def local(cls):
        return ModelSettings(
            model_url = "http://localhost:11434/v1",
            model_api_key = "ollama_local",
            model = 'qwen3:4b'
        )


def make_client(settings : ModelSettings) -> OpenAI:

    return OpenAI(
        base_url = settings.model_url,
        api_key = settings.model_api_key
    )


def generate_content(
        client: OpenAI, 
        settings: ModelSettings,
        system_prompt: str, 
        paper_text: str = None, 
        output_json: bool = False):
            
    messages = [{"role": "system", "content": system_prompt}]
    
    if paper_text:
        messages.append({"role": "user", "content": f"Here is the paper to analyze:\n\n{paper_text}"})

    # Prepare configuration
    kwargs = {
        "model": settings.model,
        "messages": messages,
        "temperature": 0.1,
    }

    if output_json:
        kwargs["response_format"] = {"type": "json_object"}

    # Execute request
    response = client.chat.completions.create(**kwargs)
    return response.choices[0].message.content
