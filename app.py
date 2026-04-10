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
import math


# PAPERS_FOLDER = "papers"
PAPERS_FOLDER = "papers_markdown\\docling"
BASE_ONTOLOGY_FILE = "ontology\\ontology_v1.json"
OUTPUT_PATH = "output"
BATCH_SIZE = 10
CONSOLIDATOR_THRESHOLD = 2
PAPER_LIMIT = 5


def consolidate_and_merge(client, ontology_group, aggregator_entries, output_file):
    
    consolidator = ConsolidatorAgent()
    consolidated_data = consolidator.run(client, aggregator_entries, output_file)
    
    normalized_mappings = {d['original_name']: d['normalized_name'] 
                           for d in consolidated_data['normalized_variable_mapping']}    
    
    normalized_definitions = {d['normalized_name']: d['normalized_definition'] 
                              for d in consolidated_data['normalized_variable_definitions']}

    existing_variables = [normalized_mappings[name] for name in ontology_group.keys()]
    
    proposed_variables = [normalized_mappings[name] 
                          for (name,defn) in aggregator_entries
                          if normalized_mappings[name] not in existing_variables]
     
    proposed_variable_counts = Counter(proposed_variables)

    new_variables = [name for name, defn in proposed_variable_counts.items() 
                          if defn >= CONSOLIDATOR_THRESHOLD]

    updated_ontology_group = {name: normalized_definitions[name] 
                              for name in existing_variables + new_variables}

    return updated_ontology_group



def run_pipeline():

    os.makedirs(OUTPUT_PATH, exist_ok=True)

    collection = PaperCollection(PAPERS_FOLDER)
    collection.papers = collection.papers[:PAPER_LIMIT]
    
    # Going through the Gemini API directly allows us to extract information from 
    # the plots/figures embedded in the pdf files. Turning this off means we 
    # go through the OpenAI "chat completions" API instead, allowing us to use any LLM
    # but papers have to be sent in Markdown format, stripped of all plots/figures.
    use_google_genai = False 

    with LLMClient(ModelSettings.gemini_flash_2_5(), use_google_genai=use_google_genai) as client:

        if use_google_genai:
            collection.sync_with_gemini(client.client)
        
        ontology = Ontology(BASE_ONTOLOGY_FILE)
        
        data_extractor = DataExtractorAgent()
        critic = CriticAgent()
        
        num_batches = math.ceil(len(collection.papers) / BATCH_SIZE)

        for batch_index in range(num_batches):
            
            batch_number = batch_index + 1
            paper_idx_start = batch_index * BATCH_SIZE
            paper_idx_end = min(paper_idx_start + BATCH_SIZE, len(collection.papers))

            batch_output_path = os.path.join(OUTPUT_PATH, f"batch_{batch_number}")
            os.makedirs(batch_output_path, exist_ok=True)

            batch = collection.papers[paper_idx_start:paper_idx_end]
            aggregator = DataAggregator(ontology)
    
            pbar = tqdm(batch)

            for paper in pbar:

                data_extractor_output_file = os.path.join(batch_output_path, f"paper_{paper.reference}.md")
                critic_output_file = os.path.join(batch_output_path, f"paper_{paper.reference}_critic.json")
                
                pbar.set_description(f"Batch {batch_number} Extracting {paper.file_name}")
                extractor_output = data_extractor.run(client, paper, ontology, data_extractor_output_file)
                
                pbar.set_description(f"Batch {batch_number} Critiquing {paper.file_name}")
                critic_output = critic.run(client, paper, ontology, extractor_output, critic_output_file)
                
                aggregator.update(critic_output)

            new_ontology = Ontology()

            print("Consolidating base materials...")

            new_ontology.base_material = consolidate_and_merge(
                client,
                ontology.base_material,
                aggregator.base_material_entries,
                os.path.join(batch_output_path, "base_material_consolidated.json")
            )

            print("Consolidating conditioned materials...")

            new_ontology.conditioned_material = consolidate_and_merge(
                client,
                ontology.conditioned_material,
                aggregator.conditioned_material_entries,
                os.path.join(batch_output_path, "conditioned_material_consolidated.json")
            )

            print("Consolidating experiments...")

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
    run_pipeline()


if __name__ == "__main__":
    main()
    print("Done")
