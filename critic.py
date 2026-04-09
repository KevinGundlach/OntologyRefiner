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
Analyze the extraction against the source paper. Your goal is to identify any important metallurgical, chemical, or environmental variables that influence corrosion pitting potential but are missing from or poorly defined in the current template.

**Guidelines:**
* **Missing Variables:** Propose variables mentioned in the text that are entirely absent from the template.
* **Ambiguous/Over-consolidated Variables:** If an existing variable definition is too broad and forces fundamentally different physical/chemical concepts to be grouped together (e.g., if "heat treatment temperature" is being used for both aging and annealing, which are distinct), propose new, specific variables to separate them.
* Provide a clear, concise definition for every proposed variable.
* Output your response STRICTLY as a JSON object matching the schema below, with no markdown formatting outside the JSON block.

**Expected JSON Schema:**

{
  "proposed_base_material_variables": [ {"name": "...", "definition": "..."} ],
  "proposed_conditioned_material_variables": [ {"name": "...", "definition": "..."} ],
  "proposed_experiment_variables": [ {"name": "...", "definition": "..."} ]
}


<extractor_template>
[Paste Extractor Template Here]
</extractor_template>

<extractor_ouptut>
[Paste Extractor Output Here]
</extractor_output>

"""

class NameDefPair(BaseModel):
    name: str
    definition: str

class OutputSchema(BaseModel):
    proposed_base_material_variables: list[NameDefPair]
    proposed_conditioned_material_variables: list[NameDefPair]
    proposed_experiment_variables: list[NameDefPair]


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
        text = text.strip()

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(text)

        return json.loads(text)


# Notes from Gemini regarding implementation.
# It highly recommends repeating parts of the system prompt after the paper text.
# May incorporate that into llm_helper if I get poor performance.

# template_string = "..." # Your current variable definitions
# extraction_string = "..." # The markdown output from the Extractor

# response = client.chat.completions.create(
#     model="qwen3.5-122b-a10b",
#     messages=[
#         {"role": "system", "content": "You are a critical Materials Science Data Architect... [Insert full System Prompt here]"},
#         {"role": "user", "content": f"""<source_research_paper>
# {paper_markdown}
# </source_research_paper>

# <current_extraction_template>
# {template_string}
# </current_extraction_template>

# <extracted_data>
# {extraction_string}
# </extracted_data>

# Analyze the <extracted_data> against the <source_research_paper>. Output your critique STRICTLY as a JSON object matching the required schema. Do not include any conversational text outside the JSON."""}
#     ],
#     temperature=0.2, # Slightly higher than the extractor to allow for analytical reasoning
#     response_format={"type": "json_object"} # If your vLLM version supports JSON mode, use this!
# )    