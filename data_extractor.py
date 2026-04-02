from paper_collection import Paper
from llm_helper import LLMClient
from ontology import Ontology
import os 

PROMPT_PREFIX = r"""
**System/Instruction Prompt:**

You are an expert Materials Scientist and Data Extraction Agent. Your task is to analyze materials science research papers and extract precise data regarding metal alloy corrosion testing, specifically focusing on factors that influence the pitting potential.

You will be provided with a research paper (which may include text, tables, and figures). Your goal is to populate the hierarchical Markdown template below. 

**Extraction Rules:**

1.  **Be Exhaustive:** Scan all text, tables, and figures. If exact numbers are not in the text, carefully estimate them from relevant plots if possible, but explicitly state when a value is an estimate.

2.  **Handle Missing Data:** If a requested variable is entirely missing, output "Not specified in text." Do not invent or hallucinate data.

3.  **Traceability:** Append a brief location tag (e.g., `[Page 3, Table 2]` or `[Section: Experimental Method]`) to your extracted values so human reviewers can verify them.

4.  **Hierarchy:** A paper may have multiple Base Materials. A Base Material may have multiple Conditioned Materials (including "As-received"). A Conditioned Material may have multiple Experiments. Repeat the Markdown sections as necessary to capture all relationships accurately.

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
