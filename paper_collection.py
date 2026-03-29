import os 
import re 
from pathlib import Path
from google import genai 
from tqdm import tqdm
from typing import List 

class PaperCollection:

    def __init__(self, from_folder:Path|str, limit:int|None = None):
            
        folder_contents = os.listdir(from_folder)

        paper_paths = [Path(os.path.join(from_folder, fn)) 
                    for fn in folder_contents]
        
        paper_paths = [p for p in paper_paths if p.is_file()]
        
        papers = [Paper(p) for p in paper_paths]

        if all([hasattr(p, "reference") for p in papers]):
            papers.sort(key=lambda p: p.reference)
        else:
            papers.sort(key=lambda p: p.name)
        
        if limit is not None:
            papers = papers[:limit]

        self.papers = papers 


    def sync_with_gemini(self, client : genai.Client):
    
        already_uploaded = [f.name for f in client.files.list()]
        all_files = [p.gemini_path for p in self.papers]
        to_upload = [f for f in all_files if f not in already_uploaded]
        
        pbar = tqdm(self.papers)

        for paper in pbar:
            pbar.set_description(f"Uploading {paper.file_name}")
            if paper.gemini_path in to_upload:
                paper.upload_to_gemini(client)


    # Needed when switching API keys.
    def delete_all(self, client : genai.Client):
        
        files = client.files.list()

        for f in files:
            client.files.delete(name=f.name)
        

class Paper:

    def __init__(self, local_path : Path|str):

        if type(local_path) is str:
            local_path = Path(local_path)
        
        if not local_path.is_file():
            raise ValueError(f"File not found: {local_path}") 

        self.local_path = local_path
        self.file_name = local_path.name
        
        # Try to extract a reference number from the beginning of the file name.
        # Gemini's picky with regard to the names of files uploaded to its Files API,
        # so I generate simple names based on the reference number.
        match_result = re.match(r"^(\d+)_.*$", self.file_name)
        
        if match_result:
            self.reference = int(match_result.group(1))
            self.gemini_name = f"reference-{self.reference}"
            self.gemini_path = f"files/{self.gemini_name}"
            self._gemini_file_descriptor = None

    def __str__(self):
        return repr(self)
    
    def __repr__(self):
        return f"Paper({repr(self.local_path)})"

    def read_all(self):
        with open(self.local_path, "r", encoding="utf-8") as f:
            return f.read()

    def upload_to_gemini(self, client : genai.Client):

        if self._gemini_file_descriptor is not None:
            return self._gemini_file_descriptor

        is_pdf = self.local_path.suffix.lower() == ".pdf"
        mime_type = "application/pdf" if is_pdf else "text/plain"

        with open(self.local_path, "rb") as f:
            self._gemini_file_descriptor = client.files.upload(
                file=f,
                config={
                    "name": self.gemini_name,
                    "mime_type": mime_type
                }
            )

        return self._gemini_file_descriptor        

    def get_gemini_file_descriptor(self, client : genai.Client):
        
        if self._gemini_file_descriptor is not None:
            return self._gemini_file_descriptor
        else:
            self._gemini_file_descriptor = client.files.get(name=self.gemini_name)
            return self._gemini_file_descriptor
