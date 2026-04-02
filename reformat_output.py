from pathlib import Path
import os
import json


def to_dictionary(list_of_dicts):
    
    tuples = [] 
    
    for d in list_of_dicts:
        tuples.extend(d.items())
    
    return dict(tuples)
    

def reformat_critic_file(json_path):
    
    content = Path(json_path).read_text(encoding="utf-8")
    json_data = json.loads(content)

    json_data['proposed_base_material_variables'] = to_dictionary(json_data['proposed_base_material_variables'])
    json_data['proposed_conditioned_material_variables'] = to_dictionary(json_data['proposed_conditioned_material_variables'])
    json_data['proposed_experiment_variables'] = to_dictionary(json_data['proposed_experiment_variables'])
    
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(json_data, f, indent=4)


def reformat_consolidator_file(json_path):

    content = Path(json_path).read_text(encoding="utf-8")
    json_data = json.loads(content)

    json_data['variable_mapping'] = to_dictionary(json_data['variable_mapping'])
    json_data['normalized_definitions'] = to_dictionary(json_data['normalized_definitions'])
    
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(json_data, f, indent=4)


def main():

    for i in range(1, 3):
        
        batch_folder = f"output\\batch_{i}"
        
        critic_files = [os.path.join(batch_folder,  f) 
                        for f in os.listdir(batch_folder) 
                        if f.endswith("_critic.json")]
        
        consolidated_base_material_file = os.path.join(batch_folder, "consolidated_base_material_variables.json")
        consolidated_conditioned_material_file = os.path.join(batch_folder, "consolidated_conditioned_material_variables.json")
        consolidated_experiment_file = os.path.join(batch_folder, "consolidated_experiment_variables.json")

        for f in critic_files:
            reformat_critic_file(f)

        reformat_consolidator_file(consolidated_base_material_file)
        reformat_consolidator_file(consolidated_conditioned_material_file)
        reformat_consolidator_file(consolidated_experiment_file)


if __name__ == "__main__":
    main()
    print("Done")
