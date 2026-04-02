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
        

# ==== After Batch 1 ====

# Replaced the original variables with consolidator-normalized ones.
# Added variables which the critic recommended at least 5 times 
# out of the batch of ten papers (reference numbers 1-10).

# BASE_MATERIAL_VARIABLES = {
#     "material_identifier": "The standard designation, trade name, commercial grade, ID, or Unified Numbering System (UNS) code used to explicitly identify the base material or alloy.",
#     "chemical_composition": "The precise chemical makeup of the alloy or base material, including trace elements, typically expressed in specific units of measure (e.g., wt%, at%).",
#     "material_classification": "A broad description or classification category defining the base material or alloy type.",
#     "microstructural_features": "Details describing the internal structure of the material, including the overall microstructure, specific secondary phases, precipitates, intermetallic compounds, and the characteristics (type, density, elemental makeup) of non-metallic inclusions.",
# }

# CONDITIONED_MATERIAL_VARIABLES = {
#     "material_identifier": "The unique name, designation, or identification code of the conditioned material under investigation.",
#     "manufacturing_process_description": "A descriptive summary of the overall preparation, manufacturing, and processing steps applied to the base material prior to specimen extraction.",    
#     "heat_treatment_parameters": "Details describing the applied thermal treatments, including temperatures, durations, and cooling methods used to condition the material microstructure.",
#     "surface_preparation_and_finish": "The comprehensive mechanical and chemical procedures applied to the specimen surface prior to testing. This includes abrasive grinding, polishing, chemical etching, pickling, and passivation techniques to remove cold-worked layers, as well as the resulting surface roughness, which critically influences localized pitting initiation.",
# }

# EXPERIMENT_VARIABLES = {
#     "experimental_test_summary": "A high-level summary of the overall experimental procedure and environmental conditions, encompassing test type, solution chemistry, and operating parameters.",
#     "stable_pitting_potential": "The extracted critical pitting potential values, including associated units of measure, at which stable localized pitting occurs.",
#     "reference_electrode": "The standard reference electrode (e.g., Saturated Calomel Electrode, Ag/AgCl) against which electrochemical potentials are measured, strictly required to standardize and interpret pitting and breakdown potentials.",
#     "polarization_scan_rate": "The continuous sweep rate (e.g., mV/hr, mV/s) or discrete step-size and holding duration applied to change the electrical potential during potentiodynamic or potentiostatic polarization testing.",
#     "electrolyte_temperature": "The exact, controlled temperature of the test solution or electrolyte during the electrochemical measurement, acting as a critical thermodynamic variable that non-linearly influences pitting potential.",
# }

# Counts:
# Base Material Counts:
# material_purity: 3
# material_form: 2

# Conditioned Material Counts:
# surface_preparation_and_finish: 9
# specimen_geometry_and_dimensions: 3
# welding_parameters: 1
# specimen_orientation: 1
# oxide_film_thickness: 1
# material_section_thickness: 1
# material_product_form: 1
# exposed_surface_area: 1
# crevice_prevention_technique: 1
# crevice_former_specification: 1

# Experiment Counts:
# reference_electrode: 8
# polarization_scan_rate: 8
# electrolyte_temperature: 6
# temperature_step_test_parameters: 4
# aeration_and_dissolved_oxygen_status: 4
# sample_mounting_and_masking: 3
# aggressive_anion_concentration: 3
# steady_state_measurement_indicator: 2
# pre_test_conditioning_and_immersion: 2
# inhibitor_concentration: 2
# electrolyte_ph: 2
# reversal_current_density: 1
# repassivating_metastable_pitting_potential: 1
# redox_potential: 1
# heavy_metal_cation_additions: 1
# critical_pitting_temperature: 1
# critical_crevice_temperature: 1
# crevice_former_specifications: 1


# ==== Original ====

# BASE_MATERIAL_VARIABLES = {
#     "identifier": "[Name or ID of the base material]",
#     "alloy composition": "[Precise chemical composition, including trace elements and units of measure, e.g., wt%, at%]",
#     "alloy type": "[Brief paragraph describing the alloy classification]",
#     "microstructure": "[Brief paragraph describing the microstructure]"
# }

# CONDITIONED_MATERIAL_VARIABLES = {
#     "identifier": "[Name or ID of the conditioned material]",
#     "process_description": "[Brief paragraph describing preparation, manufacturing, or processing]",
#     "heat_treatment": "[Brief paragraph describing applied heat treatments]"
# }

# EXPERIMENT_VARIABLES = {
#     "test_procedure": "[Full summary of the test procedure, e.g., potentiostatic polarization, scan rate]",
#     "test_solution_and_environment": "[All details including electrolyte, chloride ion concentration, pH, temperature, deaeration, etc.]",
#     "pitting_potential": "[Extracted values with units of measure]"
# }
