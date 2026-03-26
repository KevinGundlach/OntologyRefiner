from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions

def convert(pdf_path, output_path):
    print(f"Starting conversion for {pdf_path} using Docling...")
    
    # 1. Configure the pipeline explicitly for scanned science papers
    pipeline_options = PdfPipelineOptions()
    pipeline_options.do_ocr = True  # Forces Optical Character Recognition for old scans
    pipeline_options.do_table_structure = True  # Activates the TableFormer model
    pipeline_options.generate_picture_images = True # Maps captions to figures
    
    # 2. Initialize the converter with our strict PDF rules
    converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
        }
    )

    # 3. Process the entire document (Layout Analysis -> OCR -> Reassembly)
    result = converter.convert(pdf_path)
    
    # 4. Export the structured document to clean Markdown
    markdown_text = result.document.export_to_markdown()

    # Save it to your hard drive
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(markdown_text)
        
    print(f"Successfully saved structured Markdown to {output_path}")


###################
# TODO:
# I just learned that docling can also save any recognized plots as images.
# Adapt the above code accordingly and run it again.

# from docling.datamodel.document.elements import PictureItem
# import os

# # ... (Run the converter exactly as you did before) ...
# result = converter.convert(pdf_path)

# # Create a folder to hold the plots for this paper
# output_dir = "extracted_plots"
# os.makedirs(output_dir, exist_ok=True)

# # Loop through every element Docling found in the document
# pic_counter = 1
# for item, level in result.document.iterate_items():
#     # If the element is a Picture or Plot
#     if isinstance(item, PictureItem):
#         # Extract the cropped PIL image from Docling's memory
#         pil_img = item.get_image(result.document)
        
#         if pil_img is not None:
#             img_path = os.path.join(output_dir, f"plot_{pic_counter}.png")
#             pil_img.save(img_path)
#             print(f"Saved {img_path}")
#             pic_counter += 1

