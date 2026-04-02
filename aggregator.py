from ontology import Ontology
from typing import List, Tuple, Dict, Any


class DataAggregator:

    def __init__(self, ontology:Ontology):
        
        self.base_material_entries : List[Tuple[str, str]] = [] 
        self.conditioned_material_entries : List[Tuple[str, str]] = [] 
        self.experiment_entries : List[Tuple[str, str]] = [] 
        
        self.base_material_entries.extend(ontology.base_material.items())
        self.conditioned_material_entries.extend(ontology.conditioned_material.items())
        self.experiment_entries.extend(ontology.experiment.items())

    def update(self, critic_data:Any):
        self.base_material_entries.extend(critic_data['proposed_base_material_variables'].items())
        self.conditioned_material_entries.extend(critic_data['proposed_conditioned_material_variables'].items())
        self.experiment_entries.extend(critic_data['proposed_experiment_variables'].items())   

