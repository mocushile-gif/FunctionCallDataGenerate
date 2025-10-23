import os
import json
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv
load_dotenv()

def merge_pdfs(pdf_paths: List[str], output_path: Optional[str] = None,
               ):
    """
    Merge multiple PDF files into a single PDF.

    Parameters:
    - pdf_paths (List[str]): List of paths to input PDF files.
    - output_path (str, optional): Path for the output merged PDF. If not provided, will create auto-named file.

    Returns:
    - dict: Processing result information.
    """

    try:
        # Validate input
        if not pdf_paths or len(pdf_paths) < 2:
            return {"error": "At least 2 PDF files are required for merging"}
        
        # Check if all input files exist
        for pdf_path in pdf_paths:
            if not os.path.exists(pdf_path):
                return {"error": f"Input PDF file not found: {pdf_path}"}
        
        # Set output path if not provided
        if output_path is None:
            base_name = "merged_pdf"
            output_path = f"{base_name}.pdf"
        
        # Get input files information
        input_files_info = []
        total_input_size = 0
        
        for pdf_path in pdf_paths:
            file_size = os.path.getsize(pdf_path)
            total_input_size += file_size
            input_files_info.append({
                "path": pdf_path,
                "size": file_size,
                "filename": os.path.basename(pdf_path)
            })
        
        # Check if required libraries are available
        try:
            from PyPDF2 import PdfMerger
            
            # Create PDF merger
            merger = PdfMerger()
            
            # Add each PDF to the merger
            for pdf_path in pdf_paths:
                merger.append(pdf_path)
            
            # Write the merged PDF
            merger.write(output_path)
            merger.close()
            
            # Get output file information
            output_size = os.path.getsize(output_path)
            
            result = {
                "input_files": input_files_info,
                "output_path": output_path,
                "operation": "merge_pdfs",
                "parameters": {
                    "num_input_files": len(pdf_paths)
                },
                "total_input_size": total_input_size,
                "output_file_size": output_size,
                "success": True
            }
            
            return result
            
        except ImportError:
            return {"error": "PyPDF2 library is required for PDF merging"}
            
    except Exception as e:
        return {"error": f"Error merging PDFs: {str(e)}"}

if __name__ == "__main__":
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    # Example usage
    result = merge_pdfs(["./pdf_data/US_Declaration.pdf","./pdf_data/resume.pdf"])
    print(json.dumps(result, indent=2)) 