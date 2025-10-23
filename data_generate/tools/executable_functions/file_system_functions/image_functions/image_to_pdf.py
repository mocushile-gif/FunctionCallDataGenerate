import os
import json
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv
load_dotenv()

def image_to_pdf(image_paths: List[str], output_path: Optional[str] = None,
                 page_size: str = "A4", orientation: str = "portrait",
                 margin: int = 20):
    """
    Convert multiple images to a single PDF document.

    Parameters:
    - image_paths (List[str]): List of paths to input image files.
    - output_path (str, optional): Path for the output PDF file. If not provided, will create auto-named file.
    - page_size (str): Page size for the PDF. Options: "A4", "A3", "A5", "Letter", "Legal".
    - orientation (str): Page orientation. Options: "portrait", "landscape".
    - margin (int): Margin around images in pixels (0-100).

    Returns:
    - dict: Processing result information.
    """
    
    try:
        # Validate input
        if not image_paths or len(image_paths) == 0:
            return {"error": "At least one image file is required"}
        
        # Check if all input files exist
        for image_path in image_paths:
            if not os.path.exists(image_path):
                return {"error": f"Input image file not found: {image_path}"}
        
        # Validate parameters
        valid_page_sizes = ["A4", "A3", "A5", "Letter", "Legal"]
        if page_size not in valid_page_sizes:
            return {"error": f"page_size must be one of: {', '.join(valid_page_sizes)}"}
        
        if orientation not in ["portrait", "landscape"]:
            return {"error": "orientation must be one of: portrait, landscape"}
        
        if margin < 0 or margin > 100:
            return {"error": "margin must be between 0 and 100"}
        
        # Set output path if not provided
        if output_path is None:
            base_name = "images_to_pdf"
            output_path = f"{base_name}.pdf"
        
        # Get input files information
        input_files_info = []
        total_input_size = 0
        
        for image_path in image_paths:
            file_size = os.path.getsize(image_path)
            total_input_size += file_size
            input_files_info.append({
                "path": image_path,
                "size": file_size,
                "filename": os.path.basename(image_path)
            })
        
        # Check if required libraries are available
        try:
            from PIL import Image
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import A4, A3, A5, letter, legal
            from reportlab.lib.units import inch
            
            # Map page sizes to reportlab constants
            page_size_map = {
                "A4": A4,
                "A3": A3,
                "A5": A5,
                "Letter": letter,
                "Legal": legal
            }
            
            # Get page size
            pagesize = page_size_map[page_size]
            if orientation == "landscape":
                pagesize = (pagesize[1], pagesize[0])
            
            # Create PDF
            c = canvas.Canvas(output_path, pagesize=pagesize)
            
            # Process each image
            processed_images = []
            for i, image_path in enumerate(image_paths):
                try:
                    # Open image
                    with Image.open(image_path) as img:
                        original_size = img.size
                        original_mode = img.mode
                        
                        # Convert to RGB if necessary
                        if img.mode != 'RGB':
                            img = img.convert('RGB')
                        
                        # Calculate image dimensions to fit on page
                        page_width, page_height = pagesize
                        max_width = page_width - 2 * margin
                        max_height = page_height - 2 * margin
                        
                        # Calculate scaling to fit image on page
                        img_width, img_height = img.size
                        scale_x = max_width / img_width
                        scale_y = max_height / img_height
                        scale = min(scale_x, scale_y)
                        
                        # Calculate final dimensions
                        final_width = img_width * scale
                        final_height = img_height * scale
                        
                        # Calculate position to center image
                        x = (page_width - final_width) / 2
                        y = (page_height - final_height) / 2
                        
                        # Save image to temporary file
                        temp_img_path = f"temp_img_{i}.jpg"
                        img.save(temp_img_path, "JPEG", quality=95)
                        
                        # Add image to PDF
                        c.drawImage(temp_img_path, x, y, width=final_width, height=final_height)
                        
                        # Clean up temporary file
                        os.remove(temp_img_path)
                        
                        processed_images.append({
                            "index": i + 1,
                            "original_path": image_path,
                            "original_size": original_size,
                            "original_mode": original_mode,
                            "final_size": (final_width, final_height),
                            "position": (x, y)
                        })
                        
                        # Add new page if not the last image
                        if i < len(image_paths) - 1:
                            c.showPage()
                
                except Exception as e:
                    return {"error": f"Error processing image {image_path}: {str(e)}"}
            
            # Save PDF
            c.save()
            
            # Get output file information
            output_size = os.path.getsize(output_path)
            
            result = {
                "input_files": input_files_info,
                "output_path": output_path,
                "operation": "image_to_pdf",
                "parameters": {
                    "page_size": page_size,
                    "orientation": orientation,
                    "margin": margin,
                    "num_images": len(image_paths)
                },
                "total_input_size": total_input_size,
                "output_file_size": output_size,
                "processed_images": processed_images,
                "success": True
            }
            
            return result
            
        except ImportError:
            return {"error": "PIL (Pillow) and reportlab libraries are required for PDF creation"}
            
    except Exception as e:
        return {"error": f"Error converting images to PDF: {str(e)}"}


if __name__ == "__main__":
    # Example usage
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    result = image_to_pdf(["./image_data/dog.jpg", "./image_data/chat.png"], page_size="A4", orientation="portrait")
    print(json.dumps(result, indent=2)) 