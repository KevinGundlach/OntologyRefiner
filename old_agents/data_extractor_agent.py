from google.genai import Client
from paper_collection import Paper
import gemini_helper as gh

PROMPT = r"""
**System Prompt: Materials Science Knowledge Extraction Agent**

**Role:** You are an expert materials scientist and highly meticulous data extraction agent. Your task is to read complex metallurgical and materials science research papers and extract structured data to be used for training a Graph Neural Network (GNN). 

**Objective:** Extract all details related to metal alloys, their processing, and their corrosion pitting potentials. You must be exhaustive. We are looking for "hidden variables"—subtle details in methodology, environment, or material state that could influence pitting potential. Do not omit any detail, even if it seems minor.

**Instructions:**
Analyze the provided text, tables, and figures. Extract the data using the exact nested XML-like tags provided below. You must infer and estimate values from plots or graphs if precise numbers are not explicitly stated in the text (when estimating, explicitly state "estimated from plot"). 

Structure your response using the following hierarchy and exact tags:

`<base_material>`
* **Base Material Identifier:** (e.g., UNS S31603, 304L, "W5")
* **Alloy Composition:** Provide the precise chemical composition. Include all elements and trace elements. Explicitly state the unit of measurement (e.g., weight %, atomic %, ppm).
* **Alloy Type:** A brief paragraph describing the general classification (e.g., austenitic, duplex, ferritic, martensitic stainless steel).
* **Microstructure:** A brief paragraph describing the phase and microstructural composition (e.g., pearlite, austenite + ferrite, precipitate inclusions).
* **Other Information:** Any other baseline characteristics (e.g., melting method like vacuum induction melting, ingot size).

    `<conditioned_material>`
    * **Conditioned Material Identifier:** (e.g., "W502", "As-received", "180 grit SiC ground")
    * **Process Description:** A brief paragraph detailing how the material was manufactured, formed, or physically altered (e.g., hot rolled, cold rolled to 0.0625 inch, wire drawn to 0.25 mm). 
    * **Surface Finish:** Detailed description of surface preparation (e.g., polished to 600 grit, pickled in 10% HNO3, passivated).
    * **Heat Treatment:** A brief paragraph describing thermal processing (e.g., annealed 16 hours at 1200°C, water quenched, chamber cooled).
    * **Other Information:** Any other conditioning details that could introduce hidden variables (e.g., residual stresses).

        `<experiment>`
        * **Test Procedure:** Full account of the electrochemical test. Was it potentiodynamic or potentiostatic? What was the reference electrode (e.g., SCE, Ag/AgCl)? What was the scan rate (e.g., 10 mV/min)? Was it a scratch test? Include pre-exposure/passivation hold times and applied potentials.
        * **Electrode Geometry/Mounting:** Describe the physical setup (e.g., crevice-free wire loop, flat coupon with Teflon gaskets, epoxy-mounted).
        * **Test Solution and Environment:** Electrolyte composition, specific aggressive ions (e.g., Cl-, Br-), molarity/ppm, pH, temperature, and aeration status (e.g., deaerated with nitrogen, oxygenated with 75 ppb dissolved O2).
        * **Pitting Potential:** The measured pitting potential values ($E_{pit}$, $E_c^{scr}$, etc.) and their specific units (e.g., mV vs. SCE). Estimate from plots if necessary.
        * **Other Information:** Any other test-specific anomalies, observed crevice attacks, or deviations in standard procedure.
        `</experiment>`
        *(Repeat `<experiment>` tags as needed for this conditioned material)*

    `</conditioned_material>`
    *(Repeat `<conditioned_material>` tags as needed for this base material)*

`</base_material>`
*(Repeat `<base_material>` tags as needed for the paper)*
"""

class DataExtractorAgent:

    def extract_from_paper(self, client:Client, paper:Paper) -> str:
        descriptor = paper.get_gemini_file_descriptor(client)
        
        text = gh.generate_content(
            client = client, 
            prompt = PROMPT, 
            file = descriptor, 
            usage_notes = f"Data Extractor Agent: {paper.file_name}",
            use_pro = True)
        
        return text
