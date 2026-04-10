from typing import List, Tuple
from llm_helper import LLMClient
from aggregator import DataAggregator
from typing import Any
from pydantic import BaseModel
import json
import os

PROMPT_TEMPLATE = """
**System/Instruction Prompt:**

You are a highly logical Data Schema Consolidator. You will be provided with a raw JSON list of variable names and definitions proposed by various extraction agents across multiple materials science papers.

**Your Task:**
Analyze the list to identify duplicates, synonyms, and overlapping concepts. Consolidate these into a clean, normalized list of variables.

**Guidelines:**
* **Normalize Names:** Standardize the naming convention to `snake_case`. 
* **Merge Wisely:** Group clearly synonymous concepts (e.g., "solution_ph" and "electrolyte_ph"). 
* **Respect Physical Distinctions:** Do NOT merge variables if they represent fundamentally different metallurgical or chemical processes, even if they sound similar (e.g., do not merge "anodic_scan_rate" with "cathodic_scan_rate").
* **Normalize Definitions:** Combine the nuances of the proposed definitions into a single, comprehensive definition for the normalized variable.
* Output your response STRICTLY as a JSON object matching the schema below.

**Expected JSON Schema:**

{
    "normalized_variable_mapping": [ 
        {
            "original_name": "...", 
            "normalized_name": "..."
        } 
    ],

    "normalized_variable_definitions": [ 
        {
            "normalized_name": "...", 
            "normalized_definition": "..."
        } 
    ]
}

<data_variables>
[Paste Data Variables Here]
</data_variables>
"""

class NormalizedVariableMapping(BaseModel):
    original_name: str
    normalized_name: str

class NormalizedVariableDefinition(BaseModel):
    normalized_name: str
    normalized_definition: str

class OutputSchema(BaseModel):
    normalized_variable_mapping: list[NormalizedVariableMapping]
    normalized_variable_definitions: list[NormalizedVariableDefinition]

class ConsolidatorAgent:

    def run(self, client:LLMClient, variables:List[Tuple[str, str]], output_path:str) -> Any:
        
        if os.path.isfile(output_path):
            with open(output_path, "r", encoding="utf-8") as f:
                return json.load(f)

        data_variables_section = "\n".join([f"- {k}: {v}" for k, v in variables])

        prompt = PROMPT_TEMPLATE.replace("[Paste Data Variables Here]", data_variables_section)
        
        text = client.generate(prompt, response_schema=OutputSchema)
        text = text.strip()

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(text)

        return json.loads(text)
