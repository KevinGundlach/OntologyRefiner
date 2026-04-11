from paper_collection import Paper
from llm_helper import LLMClient
from ontology import Ontology
import os 

PROMPT_TEMPLATE = r"""

**System Prompt:**
You are an expert Data Modeler for Materials Science. You will be given a current Data Extraction Template consisting of categorized variables and their detailed definitions. The data extracted regards measuring the pitting potential of metal alloys. Base materials represent the raw untreated alloys. Conditioned materials represent the alloys after some conditioning process has been applied to the corresponding base material, such as heat treatment. Experiment represents all the parameters and results of a particular test on a particular conditioned material. 

**Your Mission:**
Identify variables within the template that are overly broad, compound, or "catch-all" categories and atomize them into specific, single-responsibility variables. 

**Strict Guidelines for Atomization:**
1. **Definition-Driven Splitting:** You MUST derive the new, specific variables strictly from the text of the original broad definition. Do not guess, invent, or hallucinate sub-variables based merely on the variable's name. 
   * *Example:* If the definition for `test_solution_and_environment` is *"Provide details including the electrolyte used, chloride ion concentration, and solution pH,"* you should split it into `electrolyte_type`, `chloride_ion_concentration`, and `solution_ph`. You must **not** add `solution_temperature` unless it was explicitly mentioned or strongly implied in that original definition.
2. **Target Granularity:** A variable is too broad if its definition asks for a paragraph of diverse data rather than a single distinct metric, chemical property, or qualitative state.
3. **Maintain Hierarchy:** Keep the newly atomized variables within their original categories (Base Material, Conditioned Material, Experiment).
4. **Preserve All Information:** Not all variables have to be numeric. It is acceptable if a variable's definition asks for a brief sentence, if that information cannot otherwise be fully represented as a specific numerical or categorical value.

**Output Format:**
Output the updated, atomized template as a markdown document. For each new variable, provide its `snake_case` name and a concise, single-responsibility definition.

<current_extraction_template>
[Paste Extraction Template Here]
</current_extraction_template>

"""

# Output as markdown for the time being. 
# JSON would be better, but having to output as lists of {name: ..., definition...} objects 
# would be annoying. We can't use a pydantic schema of our output format involves 
# json objects having dynamic keys, which is exactly how we use a normal python dictionary.

class RefinerAgent:

    def run(self, 
            client:LLMClient, 
            ontology:Ontology, 
            output_path:str
        ) -> str:
        
        if os.path.isfile(output_path):
            with open(output_path, "r", encoding="utf-8") as f:
                return f.read()

        prompt = PROMPT_TEMPLATE.replace("[Paste Extraction Template Here]", ontology.to_markdown())

        text = client.generate(prompt)
 
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(text)

        return text
