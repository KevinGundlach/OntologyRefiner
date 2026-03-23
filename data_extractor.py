from google.genai import Client
from paper_collection import Paper
import gemini_helper as gh
import ontology

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

EXTRACTION_TEMPLATE = r"""
# Base Material
<BASE_MATERIAL_VARIABLES_HERE>

## Conditioned Material
<CONDITIONED_MATERIAL_VARIABLES_HERE>

### Experiment
<EXPERIMENT_VARIABLES_HERE>
"""

class DataExtractorAgent:

    def __init__(self):
        
        base_material_variables = ontology.BASE_MATERIAL_VARIABLES
        conditioned_material_variables = ontology.CONDITIONED_MATERIAL_VARIABLES
        experiment_variables = ontology.EXPERIMENT_VARIABLES

        base_material_section = "\n".join([f"- {k}: {v}" for k, v in base_material_variables.items()])
        conditioned_material_section = "\n".join([f"- {k}: {v}" for k, v in conditioned_material_variables.items()])
        experiment_section = "\n".join([f"- {k}: {v}" for k, v in experiment_variables.items()])

        self.extraction_template = (EXTRACTION_TEMPLATE
            .replace("<BASE_MATERIAL_VARIABLES_HERE>", base_material_section)
            .replace("<CONDITIONED_MATERIAL_VARIABLES_HERE>", conditioned_material_section)
            .replace("<EXPERIMENT_VARIABLES_HERE>", experiment_section))
        
        self.prompt = PROMPT_PREFIX + "\n" + self.extraction_template


    def extract_from_paper(self, client:Client, paper:Paper) -> str:
        
        descriptor = paper.get_gemini_file_descriptor(client)
        
        text = gh.generate_content(
            client = client, 
            prompt = self.prompt, 
            file = descriptor, 
            use_pro = True)
        
        return text
