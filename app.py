from data_extractor import DataExtractorAgent
from critic import CriticAgent, CriticDataAggregator
from consolidator import ConsolidatorAgent
from paper_collection import PaperCollection, Paper
from pdf_to_markdown import convert
from llm_helper import LLMClient, ModelSettings


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


def aggregate_critic_output(papers):
    
    aggregator = CriticDataAggregator()

    for paper in papers:
        critic_output = read_file(f"outputs\\paper_{paper.reference}_critic.json")
        aggregator.parse(critic_output)

    return aggregator


def run_consolidator(client, papers):

    aggregator = aggregate_critic_output(papers)

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

    client = LLMClient(ModelSettings.gemini_pro(), use_google_genai=True)
    collection = PaperCollection(from_folder="papers", limit=10)
    collection.sync_with_gemini(client.client)

    for i in range(7, 10):
        paper = collection.papers[i]
        print(paper.file_name)
        print("Running extractor...")
        run_extractor(client, paper)
        print("Running critic...")
        run_critic(client, paper)
    

if __name__ == "__main__":
    main()
    print("Done")
