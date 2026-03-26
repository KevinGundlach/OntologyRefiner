from data_extractor import DataExtractorAgent
from critic import CriticAgent, CriticDataAggregator
from consolidator import ConsolidatorAgent
from paper_collection import PaperCollection, Paper
from pdf_to_markdown import convert
import gemini_helper as gh 

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

    collection = PaperCollection(from_folder="papers", limit=PAPER_LIMIT)

    print(repr([p.file_name for p in collection.papers]))

    # for paper in collection.papers:
    #     print(paper.file_name)
    #     convert(f"papers\\{paper.file_name}", f"papers_markdown\\{paper.file_name}.md")    

    # collection = PaperCollection(from_folder="papers", limit=PAPER_LIMIT)

    # with gh.make_client() as client:
    #     run_consolidator(client, collection.papers[:5])


    #     for i in range(1, 5):
    #         print(f"Processing paper {collection.papers[i].file_name}")
    #         run_extractor(client, collection.papers[i])
    #         run_critic(client, collection.papers[i])



if __name__ == "__main__":
    main()
    print("Done")
