from paper_collection import Paper
from llm_helper import LLMClient
from ontology import Ontology
import os 

PROMPT_PREFIX = r"""
**System/Instruction Prompt:**

You are an expert Materials Science Data Extractor. Your task is to extract experimental data regarding the corrosion pitting potential of metal alloys from the provided research paper to serve as a preprocessing step for a machine learning dataset.

You must output the data strictly in the plain-text Markdown template provided below. 

**Extraction Rules:**

1. **Maintain Hierarchy:** A paper may discuss multiple Base Materials. A Base Material may have multiple Conditioned Materials. A Conditioned Material may have multiple Experiments. 

2. **Duplication is Expected:** If the exact same experiment (e.g., same solution, temperature, scan rate) is performed on multiple different Conditioned Materials, **duplicate the full experiment details** under each respective Conditioned Material section. Do not use cross-references like "See Experiment 1".

3. **Absence of Data:** If a requested variable is not explicitly mentioned in the text, you MUST write "Not specified in text." Do not infer, guess, or assume standard room conditions.

4. **Completeness & Precision:** Extract quantitative data with its corresponding units (e.g., wt%, ppm, °C, mV). 

5. **Markdown Citation:** Every extracted value must include a citation. Provide the closest Markdown heading where the data was found. 

**Output Template:**
"""

class DataExtractorAgent:

    def run(self, 
            client:LLMClient, 
            paper:Paper, 
            ontology:Ontology, 
            output_path:str
        ) -> str:
        
        if os.path.isfile(output_path):
            with open(output_path, "r", encoding="utf-8") as f:
                return f.read()

        prompt = PROMPT_PREFIX + "\n" + ontology.to_markdown()

        text = client.generate(prompt, paper)
 
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(text)

        return text
