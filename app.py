from data_extractor import DataExtractorAgent
from critic import CriticAgent
from consolidator import ConsolidatorAgent
from aggregator import DataAggregator
from paper_collection import PaperCollection, Paper
from pdf_to_markdown import convert
from llm_helper import LLMClient, ModelSettings
from tqdm import tqdm
from collections import Counter
import os
import json
import ontology


def read_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def run_extractor(client, paper):
    
    extractor = DataExtractorAgent()
    text = extractor.extract_from_paper(client, paper)
    
    output_path = f"outputs\\paper_{paper.reference}.md"

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(text)


def run_critic(client, paper):

    extraction_template = DataExtractorAgent().extraction_template
    extractor_output = read_file(f"outputs\\paper_{paper.reference}.md")

    critic = CriticAgent()
    text = critic.review(client, paper, extraction_template, extractor_output)

    output_path = f"outputs\\paper_{paper.reference}_critic.json"

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(text)
    

def run_consolidator(client, aggregator, output_file):

    consolidator = ConsolidatorAgent()

    text = consolidator.consolidate(client, aggregator.entries)
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(text)
    

def aggregate_critic_data(batch_path):

    json_critic_files = os.listdir(batch_path)

    json_critic_files = [os.path.join(batch_path, file) 
                            for file in json_critic_files 
                            if file.endswith("_critic.json")]

    json_critic_files_contents = [read_file(file) for file in json_critic_files]

    base_material_aggregator = DataAggregator()
    conditioned_material_aggregator = DataAggregator()
    experiment_aggregator = DataAggregator()

    base_material_aggregator.insert(ontology.BASE_MATERIAL_VARIABLES)
    conditioned_material_aggregator.insert(ontology.CONDITIONED_MATERIAL_VARIABLES)
    experiment_aggregator.insert(ontology.EXPERIMENT_VARIABLES)

    for file_content in json_critic_files_contents:
        file_obj = json.loads(file_content)
        base_material_aggregator.insert(file_obj["proposed_base_material_variables"])
        conditioned_material_aggregator.insert(file_obj["proposed_conditioned_material_variables"])
        experiment_aggregator.insert(file_obj["proposed_experiment_variables"])

    return (
        base_material_aggregator,
        conditioned_material_aggregator,
        experiment_aggregator)


def print_counts(batch_path):

    # Definitely need to refactor this.

    (base_material_aggregator, 
     conditioned_material_aggregator,
     experiment_aggregator) =  aggregate_critic_data(batch_path)

    base_material_variables = json.loads(read_file(f"{batch_path}\\consolidated_base_material_variables.json"))
    conditioned_material_variables = json.loads(read_file(f"{batch_path}\\consolidated_conditioned_material_variables.json"))
    experiment_variables = json.loads(read_file(f"{batch_path}\\consolidated_experiment_variables.json"))

    base_material_counts = base_material_aggregator.get_normalized_entry_counts(
        base_material_variables['variable_mapping'],
        ontology.BASE_MATERIAL_VARIABLES.keys()
    )

    conditioned_material_counts = conditioned_material_aggregator.get_normalized_entry_counts(
        conditioned_material_variables['variable_mapping'],
        ontology.CONDITIONED_MATERIAL_VARIABLES.keys()
    )

    experiment_counts = experiment_aggregator.get_normalized_entry_counts(
        experiment_variables['variable_mapping'],
        ontology.EXPERIMENT_VARIABLES.keys()
    )

    base_material_counts = [(c, v) for (v, c) in base_material_counts.items()]
    base_material_counts.sort(reverse=True)

    conditioned_material_counts = [(c, v) for (v, c) in conditioned_material_counts.items()]
    conditioned_material_counts.sort(reverse=True)

    experiment_counts = [(c, v) for (v, c) in experiment_counts.items()]
    experiment_counts.sort(reverse=True)

    print("Base Material Counts:")
    for c, v in base_material_counts:
        print(f"{v}: {c}")

    print("\nConditioned Material Counts:")
    for c, v in conditioned_material_counts:
        print(f"{v}: {c}")

    print("\nExperiment Counts:")
    for c, v in experiment_counts:
        print(f"{v}: {c}")


def main():

    collection = PaperCollection("papers")
    collection.papers = collection.papers[10:20]
    
    # with LLMClient(ModelSettings.gemini_pro(), use_google_genai=True) as client:
    #     pass 

        # collection.sync_with_gemini(client.client)

        #for paper in tqdm(collection.papers):
            # run_extractor(client, paper)
            # run_critic(client, paper)

        # bma, cma, ea = aggregate_critic_data("outputs")
        
        # print("Running Consolidator...")

        # run_consolidator(client, bma, "outputs\\consolidated_base_material_variables.json")
        # run_consolidator(client, cma, "outputs\\consolidated_conditioned_material_variables.json")
        # run_consolidator(client, ea, "outputs\\consolidated_experiment_variables.json")

    print_counts("outputs")


if __name__ == "__main__":
    main()
    print("Done")
