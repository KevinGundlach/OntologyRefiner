from extractor_agent import ExtractorAgent, INITIAL_PROMPT
from critic_agent import CriticAgent
from refiner_agent import RefinerAgent
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
        
        prior_prompt = read_file(f"refined_prompt_{generation - 1}.txt")
        prior_output = read_file(f"extractor_output_{generation - 1}.txt")
        prior_report = read_file(f"critic_report_{generation - 1}.txt")

        print("Running refiner...")
        new_prompt = run_refiner(client, prior_prompt, prior_output, prior_report, f"refined_prompt_{generation}.txt")
        
        print("Running extractor...")
        new_output = run_extractor(client, paper, new_prompt, f"extractor_output_{generation}.txt")
        
        print("Running critic...")
        new_report = run_critic(client, paper, new_output, f"critic_report_{generation}.txt")
        
        print("New Critic Report Generated.")

def main():

    collection = PaperCollection(from_folder="papers", limit=PAPER_LIMIT) 
    paper = collection.papers[0]    # Just test with paper 1 for the time being.
    
    iterate(paper, 5)


if __name__ == "__main__":
    main()
    print("Done")
