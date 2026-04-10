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
        
        base_material_variables = critic_data['proposed_base_material_variables']
        conditioned_material_variables = critic_data['proposed_conditioned_material_variables']
        experiment_variables = critic_data['proposed_experiment_variables']
        
        # The critic outputs a list of dictionaries, where each dictionary has the structure:
        #
        #   {name: "...", definition: "..."}
        #
        # We want to convert this into a list of tuples
        # [(name, definition), (name, definition), ...] 

        base_material_pairs = list(zip([d['name'] for d in base_material_variables], 
                                       [d['definition'] for d in base_material_variables]))
        
        conditioned_material_pairs = list(zip([d['name'] for d in conditioned_material_variables], 
                                              [d['definition'] for d in conditioned_material_variables]))
        
        experiment_pairs = list(zip([d['name'] for d in experiment_variables], 
                                    [d['definition'] for d in experiment_variables]))
        
        self.base_material_entries.extend(base_material_pairs)
        self.conditioned_material_entries.extend(conditioned_material_pairs)
        self.experiment_entries.extend(experiment_pairs)   

