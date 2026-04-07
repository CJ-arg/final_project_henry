import os
import fitz  

def convert_pdf_to_images(pdf_path, output_folder="data/temp_images"):
    """
    Converts a PDF file into a list of images using PyMuPDF.
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    base_name = os.path.splitext(os.path.basename(pdf_path))[0]
    
    # Open the PDF document
    doc = fitz.open(pdf_path)
    image_paths = []
    
    for i in range(len(doc)):
        page = doc[i]
        # We define the zoom for high quality (200 DPI equivalent is 2x zoom)
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2)) 
        
        image_path = os.path.join(output_folder, f"{base_name}_page_{i+1}.jpg")
        pix.save(image_path)
        image_paths.append(image_path)
        
    doc.close()
    return image_paths