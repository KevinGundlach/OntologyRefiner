import torch
from PIL import Image
import pymupdf
from transformers import AutoProcessor, AutoModelForImageTextToText
from tqdm import tqdm

# I had to ask Gemini how to use GLM-OCR since I couldn't find 
# any proper documentation on it.

def convert(pdf_path, output_path):
    
    processor = AutoProcessor.from_pretrained("zai-org/GLM-OCR", use_fast=True)

    device = "cuda" if torch.cuda.is_available() else "cpu"

    model = AutoModelForImageTextToText.from_pretrained(
        "zai-org/GLM-OCR",
        dtype=torch.float32,
        device_map="auto"
    ).to(device)

    model.eval()

    doc = pymupdf.open(pdf_path)
    markdown_pages = []
    
    print(f"Using device: {model.device}")

    for page_num in tqdm(range(len(doc))):

        # Using Matrix(2, 2) effectively doubles the resolution (DPI) for better OCR
        pix = doc.get_page_pixmap(page_num, matrix=pymupdf.Matrix(2, 2))
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

        # 1. Build a structured message dictionary instead of a flat string
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "image", "image": img},
                    {
                        "type": "text", 
                        "text": "Transcribe this document as clean Markdown. Preserve tables, headings, and formulas using LaTeX where appropriate."
                    }
                ]
            }
        ]

        # 2. Let the processor apply the template and inject the correct special tokens
        inputs = processor.apply_chat_template(
            messages,
            tokenize=True,
            add_generation_prompt=True,
            return_dict=True,
            return_tensors="pt"
        ).to(device)
        
        # 3. GLM-OCR occasionally throws an error if token_type_ids are present, safely remove them
        inputs.pop("token_type_ids", None)
        
        with torch.no_grad():
            output_ids = model.generate(**inputs, max_new_tokens=8192)

        # 4. Slice the output_ids so we don't accidentally print the prompt back out
        generated_tokens = output_ids[0][inputs["input_ids"].shape[1]:]
        
        page_text = processor.decode(generated_tokens, skip_special_tokens=True)
        markdown_pages.append(f"\n{page_text}")


    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n\n---\n\n".join(markdown_pages))
