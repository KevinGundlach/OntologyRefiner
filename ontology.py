import json 
from pathlib import Path 

class Ontology:

    def __init__(self, json_file_path:str|None = None):
        
        if json_file_path is not None:
            file_contents = Path(json_file_path).read_text(encoding="utf-8")
            parsed_data = json.loads(file_contents)
            self.base_material = parsed_data['base_material']
            self.conditioned_material = parsed_data['conditioned_material']
            self.experiment = parsed_data['experiment']
        else:
            self.base_material = {}
            self.conditioned_material = {}
            self.experiment = {}

    def save(self, json_file_path:str):
        
        data = {
            "base_material": self.base_material,
            "conditioned_material": self.conditioned_material,
            "experiment": self.experiment
        }

        with open(json_file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    def to_markdown(self):
        
        markdown = "# Base Material\n"
        markdown += "\n".join([f"- {k}: {v}" for k, v in self.base_material.items()])
        markdown += "\n\n"
        markdown += "## Conditioned Material\n"
        markdown += "\n".join([f"- {k}: {v}" for k, v in self.conditioned_material.items()])
        markdown += "\n\n"
        markdown += "### Experiment\n"
        markdown += "\n".join([f"- {k}: {v}" for k, v in self.experiment.items()])  

        return markdown
