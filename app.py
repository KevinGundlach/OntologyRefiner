from extractor_agent import ExtractorAgent, INITIAL_PROMPT
from critic_agent import CriticAgent
from refiner_agent import RefinerAgent
from data_extractor_agent import DataExtractorAgent
from data_formatter_agent import DataFormatterAgent
from paper_collection import PaperCollection, Paper
import gemini_helper as gh 
import time

PAPER_LIMIT = 10

def read_file(filename):

    with open(filename) as f:
        return f.read()

def run_extractor(client, paper, prompt, output_file):
    
    extractor = ExtractorAgent(prompt)
    extraction_json = extractor.extract_from_paper(client, paper)
    
    output_path = f"outputs\\paper_{paper.reference}\\{output_file}"
    with open(output_path, "w") as f:
        f.write(extraction_json)
    
    return extraction_json

def run_critic(client, paper, extraction_json, output_file):

    critic = CriticAgent()
    report = critic.critique_extraction(client, paper, extraction_json)
    
    output_path = f"outputs\\paper_{paper.reference}\\{output_file}"
    with open(output_path, "w") as f:
        f.write(report)

    return report 

def run_refiner(client, paper, current_extractor_prompt, current_extractor_output, critic_report, output_file):

    refiner = RefinerAgent()
    
    new_extractor_prompt = refiner.refine_prompt(
        client, 
        current_extractor_prompt,
        current_extractor_output, 
        critic_report)
    
    output_path = f"outputs\\paper_{paper.reference}\\{output_file}"
    with open(output_path, "w") as f:
        f.write(new_extractor_prompt)

    return new_extractor_prompt


def iterate(paper:Paper, generation:int):
    
    with gh.make_client() as client:
        
        prior_prompt = read_file(f"outputs\\paper_{paper.reference}\\refined_prompt_{generation - 1}.txt")
        prior_output = read_file(f"outputs\\paper_{paper.reference}\\extractor_output_{generation - 1}.txt")
        prior_report = read_file(f"outputs\\paper_{paper.reference}\\critic_report_{generation - 1}.txt")

        print("Running refiner...")
        new_prompt = run_refiner(client, paper, prior_prompt, prior_output, prior_report, f"refined_prompt_{generation}.txt")

        print("Running extractor...")
        new_output = run_extractor(client, paper, new_prompt, f"extractor_output_{generation}.txt")
        
        print("Running critic...")
        new_report = run_critic(client, paper, new_output, f"critic_report_{generation}.txt")
        
        print("New Critic Report Generated.")


def generate_transcript():

    transcript = []

    for gen in range(0, 8):

        transcript.append(f"# Extractor Generation {gen} Prompt:\n")        
        if gen == 0:
            transcript.append(INITIAL_PROMPT)
        else:
            transcript.append(read_file(f"outputs\\paper_1\\refined_prompt_{gen}.txt"))
        transcript.append("\n\n")

        transcript.append(f"# Extractor Generation {gen} Output:\n")
        transcript.append(read_file("outputs\\paper_1\\extractor_output_0.txt"))
        transcript.append("\n\n")
        
        transcript.append(f"# Critic Report For Generation {gen}:\n")
        transcript.append(read_file("outputs\\paper_1\\critic_report_0.txt"))
        transcript.append("\n\n")

    with open("transcript.txt", "w") as f:
        f.write('\n'.join(transcript))

# The above functions are for running the original unrestricted extractor->critic->refinement loop.
# 
# Below are for the data extractor -> data formatter process. 

def run_data_extractor(client, paper, output_file):

    data_extractor = DataExtractorAgent()
    
    with gh.make_client() as client:
        text = data_extractor.extract_from_paper(client, paper)
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(text)

    return text 

def run_data_formatter(client, extractor_text, output_file):

    data_formatter = DataFormatterAgent()
    
    with gh.make_client() as client:
        text = data_formatter.format_text(client, extractor_text)
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(text)

    return text 


def main():

    collection = PaperCollection(from_folder="papers")
    collection.papers = [p for p in collection.papers if p.reference in [1, 2, 3, 9, 49]]
    
    with gh.make_client() as client:    
        pass         

        # collection.upload_all(client)

        # print(collection.papers[0].file_name)
        # paper_1_info = run_data_extractor(client, collection.papers[0], "outputs\\paper_1_data_api.txt")
        # run_data_formatter(client, paper_1_info, "outputs\\paper_1_json.txt")

        # print(collection.papers[1].file_name)
        # paper_2_info = run_data_extractor(client, collection.papers[1], "outputs\\paper_2_data_api.txt")
        # run_data_formatter(client, paper_2_info, "outputs\\paper_2_json.txt")   

        # print(collection.papers[2].file_name)
        # paper_3_info = run_data_extractor(client, collection.papers[2], "outputs\\paper_3_data_api.txt")
        # run_data_formatter(client, paper_3_info, "outputs\\paper_3_json.txt")

        # print(collection.papers[3].file_name)
        # paper_9_info = run_data_extractor(client, collection.papers[3], "outputs\\paper_9_data_api.txt")
        # run_data_formatter(client, paper_9_info, "outputs\\paper_9_json.txt")

        # print(collection.papers[4].file_name)
        # paper_49_info = run_data_extractor(client, collection.papers[4], "outputs\\paper_49_data_api.txt")
        # run_data_formatter(client, paper_49_info, "outputs\\paper_49_json.txt")
    

if __name__ == "__main__":
    main()
    print("Done")
