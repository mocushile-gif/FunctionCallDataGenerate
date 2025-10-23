import os
import json
from typing import Dict, Any, Optional, List
from pdf2image import convert_from_path
from PIL import Image
from dotenv import load_dotenv
load_dotenv()

def convert_pdf_to_images(pdf_path: str, output_dir: Optional[str] = None, 
                          dpi: int = 200, format: str = "PNG"):
    """
    Convert PDF pages to images.

    Parameters:
    - pdf_path (str): Path to the input PDF file.
    - output_dir (str, optional): Directory to save output images. If not provided, will create auto-named directory.
    - dpi (int): Resolution for image conversion (72-600).
    - format (str): Output image format. Options: "PNG", "JPEG", "TIFF".

    Returns:
    - dict: Processing result information.
    """
    
    try:
        # Check if input file exists
        if not os.path.exists(pdf_path):
            return {"error": f"Input PDF file not found: {pdf_path}"}
        
        # Validate parameters
        if dpi < 72 or dpi > 600:
            return {"error": "dpi must be between 72 and 600"}
        
        if format.upper() not in ["PNG", "JPEG", "TIFF"]:
            return {"error": "format must be one of: PNG, JPEG, TIFF"}
        
        # Set output directory if not provided
        if output_dir is None:
            base_name = os.path.splitext(pdf_path)[0]
            output_dir = f"{base_name}_pages"
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Get file information
        file_size = os.path.getsize(pdf_path)

        # Convert PDF to images
        images = convert_from_path(pdf_path, dpi=dpi)
            
        # Save images
        output_files = []
        for i, image in enumerate(images):
            page_num = i + 1
            output_filename = f"page_{page_num:03d}.{format.lower()}"
            output_filepath = os.path.join(output_dir, output_filename)
            
            # Save image
            if format.upper() == "JPEG":
                image.save(output_filepath, "JPEG", quality=95)
            else:
                image.save(output_filepath, format.upper())
            
            output_files.append({
                "page": page_num,
                "filename": output_filename,
                "filepath": output_filepath,
                "size": os.path.getsize(output_filepath),
                "dimensions": image.size
            })
        
        # Calculate total output size
        total_output_size = sum(f["size"] for f in output_files)
        
        result = {
            "input_path": pdf_path,
            "output_dir": output_dir,
            "operation": "convert_pdf_to_images",
            "parameters": {
                "dpi": dpi,
                "format": format.upper()
            },
            "input_file_size": file_size,
            "total_output_size": total_output_size,
            "num_pages": len(images),
            "output_files": output_files,
            "success": True
        }
        
        return result
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": f"Error converting PDF: {str(e)}"}

if __name__ == "__main__":
    # Example usage
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    result = convert_pdf_to_images("./pdf_data/paper.pdf", dpi=200, format="PNG")
    print(json.dumps(result, indent=2)) 