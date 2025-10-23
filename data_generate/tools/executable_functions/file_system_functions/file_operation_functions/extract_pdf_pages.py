import os
import json
from typing import Dict, Any, Optional, List, Union
from PyPDF2 import PdfReader, PdfWriter
from PIL import Image
import fitz  # PyMuPDF
from dotenv import load_dotenv
load_dotenv()

def extract_pdf_pages(input_path: str, output_path: str = None, 
                     page_numbers: Optional[List[int]] = None, 
                     page_range: Optional[str] = None,
                     output_format: str = "pdf"):
    """
    Extract specific pages from a PDF file.
    
    Parameters:
    - input_path (str): Path to input PDF file
    - output_path (str): Path for output file (optional, auto-generated if not provided)
    - page_numbers (list): List of specific page numbers to extract (1-based indexing)
    - page_range (str): Page range in format "start-end" (e.g., "1-5", "3-")
    - output_format (str): Output format ("pdf", "images")
    
    Returns:
    - dict: Extraction result information
    """

    try:
        # Validate parameters
        if not input_path or not os.path.exists(input_path):
            return {"error": "Input PDF file not found"}
        
        if not input_path.lower().endswith('.pdf'):
            return {"error": "Input file must be a PDF"}
        
        if output_format not in ["pdf", "images"]:
            return {"error": "Output format must be 'pdf' or 'images'"}

        # Read PDF
        reader = PdfReader(input_path)
        total_pages = len(reader.pages)
        
        # Determine pages to extract
        pages_to_extract = []
        
        if page_numbers:
            # Extract specific page numbers
            for page_num in page_numbers:
                if 1 <= page_num <= total_pages:
                    pages_to_extract.append(page_num - 1)  # Convert to 0-based indexing
                else:
                    return {"error": f"Page number {page_num} is out of range (1-{total_pages})"}
        
        elif page_range:
            # Extract page range
            try:
                if '-' in page_range:
                    start, end = page_range.split('-')
                    start = int(start) if start else 1
                    end = int(end) if end else total_pages
                    
                    if start < 1 or end > total_pages or start > end:
                        return {"error": f"Invalid page range: {page_range}. The range must be between 0 and {total_pages}, inclusive."}
                    
                    pages_to_extract = list(range(start - 1, end))  # Convert to 0-based indexing
                else:
                    # Single page
                    page_num = int(page_range)
                    if 1 <= page_num <= total_pages:
                        pages_to_extract = [page_num - 1]
                    else:
                        return {"error": f"Page number {page_num} is out of range (1-{total_pages})"}
            except ValueError:
                return {"error": f"Invalid page range format: {page_range}"}
        
        else:
            # Extract all pages
            pages_to_extract = list(range(total_pages))
        
        if not pages_to_extract:
            return {"error": "No pages to extract"}
        
        # Set output path if not provided
        if not output_path:
            base_name = os.path.splitext(os.path.basename(input_path))[0]
            if output_format == "pdf":
                output_path = f"{base_name}_extracted.pdf"
            else:
                output_path = f"{base_name}_extracted"
        
        result = {
            "input_file": input_path,
            "output_path": output_path,
            "total_pages": total_pages,
            "extracted_pages": [p + 1 for p in pages_to_extract],  # Convert back to 1-based
            "output_format": output_format,
            "operation": "extract_pdf_pages",
            "parameters": {
                "page_numbers": page_numbers,
                "page_range": page_range,
                "output_format": output_format
            },
            "success": True
        }
        
        if output_format == "pdf":
            # Extract pages as PDF
            writer = PdfWriter()
            
            for page_index in pages_to_extract:
                writer.add_page(reader.pages[page_index])
            
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
            
            result["output_size"] = os.path.getsize(output_path)
            result["extraction_type"] = "pdf_pages"
            
        else:
            # Extract pages as images
            doc = fitz.open(input_path)
            image_files = []
            
            for i, page_index in enumerate(pages_to_extract):
                page = doc.load_page(page_index)
                mat = fitz.Matrix(2.0, 2.0)  # 2x zoom for better quality
                pix = page.get_pixmap(matrix=mat)
                
                image_filename = f"{output_path}_page_{page_index + 1}.png"
                pix.save(image_filename)
                image_files.append(image_filename)
            
            doc.close()
            
            result["image_files"] = image_files
            result["total_images"] = len(image_files)
            result["extraction_type"] = "page_images"
        
        return result
        
    except Exception as e:
        return {"error": f"Error extracting PDF pages: {str(e)}"}


if __name__ == "__main__":
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    # Example usage
    result = extract_pdf_pages("./pdf_data/order.pdf", page_range="1-2", output_format="pdf")
    print(json.dumps(result, indent=2)) 