from data_extractor import DataExtractorAgent
from critic import CriticAgent
from consolidator import ConsolidatorAgent
from aggregator import DataAggregator
from paper_collection import PaperCollection, Paper
from pdf_to_markdown import convert
from llm_helper import LLMClient, ModelSettings
from tqdm import tqdm
from collections import Counter
from ontology import Ontology
from pathlib import Path
import os
import json


PAPERS_FOLDER = "papers"
BASE_ONTOLOGY_FILE = "ontology\\ontology_v1.json"
OUTPUT_PATH = "output"
BATCH_SIZE = 10
CONSOLIDATOR_THRESHOLD = 5


def consolidate_and_merge(client, ontology_group, aggregator_entries, output_file):
    
    consolidator = ConsolidatorAgent()
    consolidated_data = consolidator.run(client, aggregator_entries, output_file)
    
    normalized_mappings = consolidated_data['variable_mapping']

    normalized_mappings = {name: defn 
                           for dic in normalized_mappings 
                           for name, defn in dic.items()}
    
    normalized_definitions = consolidated_data['normalized_definitions']

    normalized_definitions = {name: defn 
                              for dic in normalized_definitions 
                              for name, defn in dic.items()}

    existing_variables = [normalized_mappings[name] for name in ontology_group.keys()]
    
    proposed_variables = [normalized_mappings[name] 
                          for (name,defn) in aggregator_entries
                          if normalized_mappings[name] not in existing_variables]
     
    proposed_variable_counts = Counter(proposed_variables)

    new_variables = [name for name, defn in proposed_variable_counts.items() 
                          if defn >= CONSOLIDATOR_THRESHOLD]

    updated_ontology_group = [(name, normalized_definitions[name]) 
                              for name in proposed_variables + new_variables]

    return updated_ontology_group



def run():

    os.makedirs(OUTPUT_PATH, exist_ok=True)

    collection = PaperCollection(PAPERS_FOLDER)
    
    with LLMClient(ModelSettings.gemini_pro(), use_google_genai=True) as client:

        collection.sync_with_gemini(client.client)
        ontology = Ontology(BASE_ONTOLOGY_FILE)
        
        data_extractor = DataExtractorAgent()
        critic = CriticAgent()
        
        for batch_number in range(0, len(collection.papers), BATCH_SIZE):

            batch_output_path = os.path.join(OUTPUT_PATH, f"batch_{batch_number}")
            os.makedirs(batch_output_path, exist_ok=True)

            batch = collection.papers[batch_number:batch_number+BATCH_SIZE]
            aggregator = DataAggregator(ontology)
    
            pbar = tqdm(batch)

            for paper in pbar:

                data_extractor_output_file = os.path.join(batch_output_path, f"paper_{paper.reference}.md")
                critic_output_file = os.path.join(batch_output_path, f"paper_{paper.reference}_critic.json")
                
                pbar.set_description(f"Batch {batch_number} Extracting...")
                extractor_output = data_extractor.run(client, paper, ontology, data_extractor_output_file)
                
                pbar.set_description(f"Batch {batch_number} Critiquing...")
                critic_output = critic.run(client, paper, ontology, extractor_output, critic_output_file)
                
                aggregator.update(critic_output)

            new_ontology = Ontology()

            new_ontology.base_material = consolidate_and_merge(
                client,
                ontology.base_material,
                aggregator.base_material_entries,
                os.path.join(batch_output_path, "base_material_consolidated.json")
            )

            new_ontology.conditioned_material = consolidate_and_merge(
                client,
                ontology.conditioned_material,
                aggregator.conditioned_material_entries,
                os.path.join(batch_output_path, "conditioned_material_consolidated.json")
            )

            new_ontology.experiment = consolidate_and_merge(
                client,
                ontology.experiment,
                aggregator.experiment_entries,
                os.path.join(batch_output_path, "experiment_consolidated.json")
            )

            ontology_output_file = os.path.join(batch_output_path, f"new_ontology.json")
            new_ontology.save(ontology_output_file)

            ontology = new_ontology


def main():
    pass


if __name__ == "__main__":
    main()
    print("Done")
