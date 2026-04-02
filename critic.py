from paper_collection import Paper
from llm_helper import LLMClient 
from ontology import Ontology
from typing import Any
from pydantic import BaseModel
import json
import os

PROMPT_TEMPLATE = r"""
**System/Instruction Prompt:**

You are an expert Materials Science Data Critic. Your job is to identify critical variables affecting the corrosion pitting potential of metal alloys that the current extraction schema missed.

You will be provided with three inputs:
1. The original research paper.
2. The current extraction template (the variables currently being asked for).
3. The Data Extractor's output for this paper.

**Your Task:**
Analyze the paper and identify any environmental, metallurgical, or procedural variables mentioned by the authors that influence the pitting potential but are missing from the current template. Look for things like surface finish, sample geometry, reference electrode type, cold working percentage, flow velocity, or specific inhibitors. Also, identify if existing variables need their definitions refined for better precision.

**Output Constraints:**
You must output a valid JSON object strictly matching the structure below. Do not include markdown formatting or extra text outside the JSON object.

```json
{
    "proposed_base_material_variables": {
        "example_variable_name_1": "clear, concise definition of what this variable measures",
        "example_variable_name_2": "clear, concise definition of what this variable measures"
    },
    "proposed_conditioned_material_variables": {
        "example_variable_name_3": "clear, concise definition..."
    },
    "proposed_experiment_variables": {
        "example_variable_name_4": "clear, concise definition..."
    }
}
```

<extractor_template>
[Paste Extractor Template Here]
</extractor_template>

<extractor_ouptut>
[Paste Extractor Output Here]
</extractor_output>

"""

class OutputSchema(BaseModel):
    proposed_base_material_variables: dict[str, str]
    proposed_conditioned_material_variables: dict[str, str]
    proposed_experiment_variables: dict[str, str]


class CriticAgent:

    def run(self, 
            client:LLMClient, 
            paper:Paper, 
            ont:Ontology, 
            extractor_output:str,
            output_path:str
        ) -> Any:

        if os.path.isfile(output_path):
            with open(output_path, "r", encoding="utf-8") as f:
                return json.load(f)

        prompt = (PROMPT_TEMPLATE.replace("[Paste Extractor Template Here]", ont.to_markdown())
                                 .replace("[Paste Extractor Output Here]", extractor_output))
                
        text = client.generate(prompt, paper, response_schema=OutputSchema)
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(text)

        return json.loads(text)
