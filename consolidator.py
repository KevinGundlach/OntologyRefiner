from typing import List, Tuple
from llm_helper import LLMClient
from aggregator import DataAggregator
from typing import Any
import json

PROMPT_TEMPLATE = """
**System/Instruction Prompt:**

You are an Ontology Consolidation Agent. Your task is to clean, deduplicate, and standardize a list of proposed data variables collected from various research papers.

You will be provided with a JSON list of key-value pairs representing proposed variable names and their definitions. Because these were generated across different papers, many variables will be semantic duplicates (e.g., "solution_temp", "electrolyte_temperature", and "test_temp" all mean the same thing).

**Your Task:**
1. Group all semantic duplicates together.
2. Assign a single, highly descriptive "normalized name" to each group.
3. Create a single "normalized definition" that captures the nuances of the merged variables.

**Output Constraints:**
You must output a valid JSON object strictly matching the structure below. Every originally proposed variable name must be mapped to exactly one normalized name.

```json
{
    "variable_mapping": [
        {"original_variable_name_1": "normalized_name_A"},
        {"original_variable_name_2": "normalized_name_A"},
        {"original_variable_name_3": "normalized_name_B"}
    ],
    "normalized_definitions": [
        {"normalized_name_A": "Comprehensive definition incorporating the nuances of the grouped variables."},
        {"normalized_name_B": "Comprehensive definition incorporating the nuances of the grouped variables."}
    ]
}
```

<data_variables>
[Paste Data Variables Here]
</data_variables>

"""


class ConsolidatorAgent:

    def run(self, client:LLMClient, variables:List[Tuple[str, str]], output_path:str|None=None) -> Any:
        
        data_variables_section = "\n".join([f"- {k}: {v}" for k, v in variables])

        prompt = PROMPT_TEMPLATE.replace("[Paste Data Variables Here]", data_variables_section)
        
        text = client.generate(prompt, output_json=True)
        
        if output_path is not None:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(text)

        return json.loads(text)

