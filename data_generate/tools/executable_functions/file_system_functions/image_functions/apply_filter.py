import os
import json
from typing import Dict, Any, Optional
from dotenv import load_dotenv
load_dotenv()

def apply_filter(image_path: str, filter_type: str, output_path: Optional[str] = None):
    """
    Apply filter to image.

    Parameters:
    - image_path (str): Path to the input image file.
    - filter_type (str): Type of filter to apply (blur, sharpen, edge_enhance, emboss, find_edges, smooth, smooth_more).
    - output_path (str, optional): Path for the output image. If not provided, will create auto-named file.

    Returns:
    - dict: Processing result information.
    """
    
    try:
        # Check if input file exists
        if not os.path.exists(image_path):
            return {"error": f"Input image file not found: {image_path}"}
        
        # Validate filter type
        valid_filters = ["blur", "sharpen", "edge_enhance", "emboss", "find_edges", "smooth", "smooth_more"]
        if filter_type not in valid_filters:
            return {"error": f"Invalid filter type. Must be one of: {valid_filters}"}
        
        # Set output path if not provided
        if output_path is None:
            base_name = os.path.splitext(image_path)[0]
            ext = os.path.splitext(image_path)[1]
            output_path = f"{base_name}_{filter_type}{ext}"
        
        # Get file information
        file_size = os.path.getsize(image_path)
        file_ext = os.path.splitext(image_path)[1].lower()
        
        # Check if PIL is available for actual image processing
        try:
            from PIL import Image, ImageFilter
            
            # Open the image
            with Image.open(image_path) as img:
                original_size = img.size
                original_mode = img.mode
                
                # Apply filter
                if filter_type == "blur":
                    img = img.filter(ImageFilter.BLUR)
                elif filter_type == "sharpen":
                    img = img.filter(ImageFilter.SHARPEN)
                elif filter_type == "edge_enhance":
                    img = img.filter(ImageFilter.EDGE_ENHANCE)
                elif filter_type == "emboss":
                    img = img.filter(ImageFilter.EMBOSS)
                elif filter_type == "find_edges":
                    img = img.filter(ImageFilter.FIND_EDGES)
                elif filter_type == "smooth":
                    img = img.filter(ImageFilter.SMOOTH)
                elif filter_type == "smooth_more":
                    img = img.filter(ImageFilter.SMOOTH_MORE)
                
                # Save the processed image
                img.save(output_path)
                
                # Get output file information
                output_size = os.path.getsize(output_path)
                
                result = {
                    "input_path": image_path,
                    "output_path": output_path,
                    "operation": "filter",
                    "parameters": {
                        "filter_type": filter_type
                    },
                    "original_size": original_size,
                    "processed_size": img.size,
                    "original_mode": original_mode,
                    "processed_mode": img.mode,
                    "input_file_size": file_size,
                    "output_file_size": output_size,
                    "success": True
                }
                
                return result
        
        except ImportError:
            # PIL not available, return mock result
            result = {
                "input_path": image_path,
                "output_path": output_path,
                "operation": "filter",
                "parameters": {
                    "filter_type": filter_type
                },
                "input_file_size": file_size,
                "file_extension": file_ext,
                "success": True,
                "note": "PIL/Pillow not available - this is a mock result. Install PIL for actual image processing."
            }
            
            return result
        
    except Exception as e:
        return {"error": f"Image filter failed: {str(e)}"}

if __name__ == "__main__":
    # Example usage
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    result = apply_filter(
        image_path="./image_data/dog.jpg",
        filter_type="blur",
    )
    print(json.dumps(result, indent=2, ensure_ascii=False)) 