# Run on Google Colab.
# To install docling and force the GPU-accelerated ONNX runtime
# !pip install docling onnxruntime-gpu

from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.datamodel.document import PictureItem
from pathlib import Path 

def convert(pdf_path : str|Path):
    
    if type(pdf_path) is str:
        pdf_path = Path(pdf_path)

    markdown_path = pdf_path.with_suffix(".md")
    images_folder = pdf_path.with_name(f"plots - {pdf_path.stem}")
    images_folder.mkdir(exist_ok=True)
    
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
    with open(markdown_path, "w", encoding="utf-8") as f:
        f.write(markdown_text)
            
    # Loop through every element Docling found in the document
    pic_counter = 1

    for item, level in result.document.iterate_items():
        
        # If the element is a Picture or Plot
        if isinstance(item, PictureItem):
            
            # Extract the cropped PIL image from Docling's memory
            pil_img = item.get_image(result.document)
            
            if pil_img is not None:
                img_filename = f"plot_{pic_counter}.png"
                img_path = images_folder / img_filename
                pil_img.save(img_path)
                pic_counter += 1        
