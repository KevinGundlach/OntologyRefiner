from data_extractor import DataExtractorAgent
from critic import CriticAgent
from consolidator import ConsolidatorAgent
from aggregator import CriticDataAggregator
from paper_collection import PaperCollection, Paper
from pdf_to_markdown import convert
from llm_helper import LLMClient, ModelSettings
from tqdm import tqdm
import os
import json


PAPER_LIMIT = 10

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


def aggregate_critic_output(critic_json_files):
    
    aggregator = CriticDataAggregator()

    pbar = tqdm(critic_json_files)

    # If there's a parsing error, this helps to see which file got corrupted.
    for file in pbar:
        pbar.set_description(file)
        critic_output = read_file(file)
        aggregator.parse(critic_output)

    return aggregator
    

def run_consolidator(client, aggregator):

    consolidator = ConsolidatorAgent()

    print("Consolidating Base Material Variables...")
    text = consolidator.consolidate(client, aggregator.proposed_base_material_variables)
    with open("outputs\\consolidated_base_material_variables.json", "w", encoding="utf-8") as f:
        f.write(text)

    print("Consolidating Conditioned Material Variables...")
    text = consolidator.consolidate(client, aggregator.proposed_conditioned_material_variables)
    with open("outputs\\consolidated_conditioned_material_variables.json", "w", encoding="utf-8") as f:
        f.write(text)
    
    print("Consolidating Experiment Variables...")
    text = consolidator.consolidate(client, aggregator.proposed_experiment_variables)
    with open("outputs\\consolidated_experiment_variables.json", "w", encoding="utf-8") as f:
        f.write(text)


def main():

    
    json_critic_files = os.listdir("outputs\\gemini_pdf")

    json_critic_files = [f"outputs\\gemini_pdf\\{file}" 
                            for file in json_critic_files 
                            if file.endswith("_critic.json")]
    
    aggregator = aggregate_critic_output(json_critic_files)
    
    # with LLMClient(ModelSettings.gemini_pro(), use_google_genai=True) as client:
    #     run_consolidator(client, aggregator)


if __name__ == "__main__":
    main()
    print("Done")
