from ontology import BASE_MATERIAL_VARIABLES, CONDITIONED_MATERIAL_VARIABLES, EXPERIMENT_VARIABLES
import json


class CriticDataAggregator:

    def __init__(self, init_with_existing_ontology:bool = True):
        self.proposed_base_material_variables = []
        self.proposed_conditioned_material_variables = []
        self.proposed_experiment_variables = []

        if init_with_existing_ontology:
            self.proposed_base_material_variables.extend(BASE_MATERIAL_VARIABLES.items())
            self.proposed_conditioned_material_variables.extend(CONDITIONED_MATERIAL_VARIABLES.items())
            self.proposed_experiment_variables.extend(EXPERIMENT_VARIABLES.items())


    def parse(self, critic_json):

        # The schema should be a list of dictionaries, where each dictionary 
        # has just one key (the variable name) and one value (the definition).
        critic_data = json.loads(critic_json)

        # Here I'm transforming it into a list of tuples instead of dictionaries.

        for definition in critic_data["proposed_base_material_variables"]:
            self.proposed_base_material_variables.extend(definition.items())

        for definition in critic_data["proposed_conditioned_material_variables"]:
            self.proposed_conditioned_material_variables.extend(definition.items())

        for definition in critic_data["proposed_experiment_variables"]:
            self.proposed_experiment_variables.extend(definition.items())

