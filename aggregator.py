from ontology import Ontology
from typing import List, Tuple, Dict, Any


class DataAggregator:

    def __init__(self, ontology:Ontology):
        self.base_material_entries = to_tuple_list(ontology.base_material)
        self.conditioned_material_entries = to_tuple_list(ontology.conditioned_material)
        self.experiment_entries = to_tuple_list(ontology.experiment)

    def update(self, critic_data:Any):
        self.base_material_entries.extend(to_tuple_list(critic_data['proposed_base_material_variables']))
        self.conditioned_material_entries.extend(to_tuple_list(critic_data['proposed_conditioned_material_variables']))
        self.experiment_entries.extend(to_tuple_list(critic_data['proposed_experiment_variables']))   


# For the moment, the critic and consolidator output the proposed 
# variables as lists of singleton dictionaries. This was intended
# to handle the possibility of multiple variables having the same 
# name but different definitions. In retrospect, that maybe wasn't
# so important and a simple dictionary might have been better.

# to_tuple_list converts from whatever structure we choose for the 
# agents into a list of (name, definition) pairs.

def to_tuple_list(
        data : Tuple[str, str]
             | List[Tuple[str, str]]
             | Dict[str, str]
             | List[Dict[str, str]]
    ) -> List[Tuple[str, str]]:

    result = [] 

    if type(data) is tuple or type(data) is dict:
        data = [data]

    for entry in data:
        
        if type(entry) is tuple:
            result.append(entry)
        elif type(entry) is dict:
            result.extend(entry.items())
        else:
            raise ValueError(f"Unrecognized entry type: {type(entry)}.")

    return result 


