import os
from openai import OpenAI
from google import genai 
from google.genai import types
from google.genai.types import File 
from dataclasses import dataclass
from paper_collection import Paper 

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


class LLMClient:

    def __init__(self, settings:ModelSettings, use_google_genai:bool=False):
        
        if use_google_genai:
            self.client = genai.Client(api_key=settings.model_api_key)
        else:
            self.client = OpenAI(
                base_url = settings.model_url,
                api_key = settings.model_api_key
            )
        
        self.settings = settings 
        self.use_google_genai = use_google_genai

    def __enter__(self):
        
        if hasattr(self.client, "__enter__"):
            self.client.__enter__()
        
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        
        if hasattr(self.client, "__exit__"):
            return self.client.__exit__(exc_type, exc_val, exc_tb)
        elif hasattr(self.client, "close"):
            self.client.close()
            
        return False

    def generate(self, prompt:str, paper:Paper|None=None, output_json:bool=False):
        if self.use_google_genai:
            return self._generate_genai(prompt, paper, output_json)
        else:
            return self._generate_openai(prompt, paper, output_json) 

    def _generate_genai(self, prompt:str, paper:Paper|None=None, output_json:bool=False):
        """
        Uses Google's genai API to submit pdf files directly to Gemini.
        """
        pass 

        if paper is None:
            contents = [prompt]        
        else:
            contents = [paper.get_gemini_file_descriptor(), prompt]

        model = self.settings.model

        thinking_config = types.ThinkingConfig(thinking_level="high")
        response_mime_type = "application/json" if output_json else None

        generate_content_config = types.GenerateContentConfig(
            thinking_config=thinking_config,
            response_mime_type=response_mime_type
        )
        
        response = self.client.models.generate_content(
            model=model,
            contents=contents,
            config=generate_content_config
        )

        return response.text

    def _generate_openai(self, prompt:str, paper:Paper|None=None, output_json:bool=False):
        """
        Uses OpenAI API to connect to any compatible LLM endpoint - 
        whether that's Gemini, ChatGPT, Ollama, vLLM, etc... 
        Requires submitted files to be in plain-text format
        (e.g., Markdown) rather than PDF.
        """

        # Use the chat completions api instead of the new responses API 
        # since we're not actually connecting to ChatGPT - we're connecting
        # to Ollama, Gemini, and perhaps vLLM (when we move to the Dais cluster).
        # They're all compatible with the older API. 

        messages = [{"role": "system", "content": prompt}]
        
        if paper is not None:
            paper_text = paper.read_all()
            messages.append({"role": "user", "content": f"Here is the paper to analyze:\n\n{paper_text}"})

        # Prepare configuration
        kwargs = {
            "model": self.settings.model,
            "messages": messages,
            "temperature": 0.1,
        }

        if output_json:
            kwargs["response_format"] = {"type": "json_object"}

        # Execute request
        response = self.client.chat.completions.create(**kwargs)
        
        return response.choices[0].message.content
