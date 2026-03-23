import pathlib 
import os 
import re 
from google import genai 
from tqdm import tqdm
from typing import List 

def parse_reference_number(filename):

    match_result = re.match(r"^(\d+)_.*$", filename)
        
    if not match_result:
        raise ValueError("File name does not begin with reference number.")

    return int(match_result.group(1))


class PaperCollection:

    def __init__(self, 
                 from_folder:str|None = None, 
                 from_files:List[str]|None = None, 
                 limit:int|None = None):
        
        if from_folder is None and from_files is None:
            raise ValueError("Must specify either from_folder or from_files.")

        if from_folder is not None and from_files is not None:
            raise ValueError("Cannot specify both from_folder and from_files.")

        if from_folder is not None:
            
            file_names = os.listdir(from_folder)
            
            from_files = [os.path.join(from_folder, fn) 
                          for fn in file_names 
                          if fn.lower().endswith(".pdf")]
        
        papers = [Paper(p) for p in from_files]
        papers.sort(key=lambda p: p.reference)
        
        if limit is not None:
            papers = papers[:limit]

        self.papers = papers 

    def update_gemini_file_descriptors(self, client : genai.Client):        
        
        descriptors = list(client.files.list())
        already_uploaded = [f.name for f in descriptors]
        
        for paper in self.papers:
            if paper.gemini_path in already_uploaded:
                idx = already_uploaded.index(paper.gemini_path)
                paper.gemini_file_descriptor = descriptors[idx]

    def list_uploaded(self, client : genai.Client):
        already_uploaded = [f.name for f in client.files.list()]
        return already_uploaded

    def upload_all(self, client : genai.Client):

        already_uploaded = [f.name for f in client.files.list()]
        all_files = [p.gemini_path for p in self.papers]
        to_upload = [f for f in all_files if f not in already_uploaded]
        
        pbar = tqdm(self.papers)

        for paper in pbar:
            pbar.set_description(f"Uploading {paper.file_name}")
            if paper.gemini_path in to_upload:
                with open(paper.local_path, "rb") as f:
                    paper.gemini_file_descriptor = client.files.upload(
                        file=f,
                        config={
                            "name": paper.gemini_name,
                            "mime_type": "application/pdf"
                        }
                    )

    # Needed when switching API keys.
    def delete_all(self, client : genai.Client):
        
        files = client.files.list()

        for f in files:
            client.files.delete(name=f.name)
        

class Paper:

    def __init__(self, local_path : str):

        local_path_info = pathlib.Path(local_path)
        
        if not local_path_info.is_file():
            raise ValueError(f"File not found: {local_path}") 
        
        if not local_path_info.suffix.lower() == ".pdf":
            raise ValueError(f"Not a PDF file: {local_path}")
       
        self.local_path = local_path
        self.file_name = local_path_info.name
        self.reference = parse_reference_number(self.file_name)
        self.gemini_name = f"reference-{self.reference}"
        self.gemini_path = f"files/{self.gemini_name}"
        self.gemini_file_descriptor = None 

    def __str__(self):
        return repr(self)
    
    def __repr__(self):
        return f"Paper({repr(self.local_path)})"

    def get_gemini_file_descriptor(self, client : genai.Client):
        
        if self.gemini_file_descriptor is not None:
            return self.gemini_file_descriptor
        else:
            self.gemini_file_descriptor = client.files.get(name=self.gemini_name)
            return self.gemini_file_descriptor
