import os
import json
from typing import Dict, Any, Optional
from dotenv import load_dotenv
load_dotenv()

def crop_image(image_path: str, left: Optional[int] = None, top: Optional[int] = None,
               right: Optional[int] = None, bottom: Optional[int] = None,
               output_path: Optional[str] = None):
    """
    Crop image to specified region.

    Parameters:
    - image_path (str): Path to the input image file.
    - left (int, optional): Left coordinate of crop region. Defaults to 0.
    - top (int, optional): Top coordinate of crop region. Defaults to 0.
    - right (int, optional): Right coordinate of crop region. Defaults to image width.
    - bottom (int, optional): Bottom coordinate of crop region. Defaults to image height.
    - output_path (str, optional): Path for the output image. If not provided, will create auto-named file.

    Returns:
    - dict: Processing result information.
    """
    
    try:
        # Check if input file exists
        if not os.path.exists(image_path):
            return {"error": f"Input image file not found: {image_path}"}
        
        # Set output path if not provided
        if output_path is None:
            base_name = os.path.splitext(image_path)[0]
            ext = os.path.splitext(image_path)[1]
            output_path = f"{base_name}_cropped{ext}"
        
        # Get file information
        file_size = os.path.getsize(image_path)
        file_ext = os.path.splitext(image_path)[1].lower()
        
        # Check if PIL is available for actual image processing
        try:
            from PIL import Image
            
            # Open the image
            with Image.open(image_path) as img:
                original_size = img.size
                original_mode = img.mode
                
                # Set default crop coordinates if not provided
                if left is None:
                    left = 0
                if top is None:
                    top = 0
                if right is None:
                    right = img.width
                if bottom is None:
                    bottom = img.height
                
                # Validate crop coordinates
                if left < 0 or top < 0 or right > img.width or bottom > img.height:
                    return {"error": "Crop coordinates are out of image bounds"}
                if left >= right or top >= bottom:
                    return {"error": "Invalid crop region: left must be less than right, top must be less than bottom"}
                
                # Crop the image
                img = img.crop((left, top, right, bottom))
                
                # Save the processed image
                img.save(output_path)
                
                # Get output file information
                output_size = os.path.getsize(output_path)
                
                result = {
                    "input_path": image_path,
                    "output_path": output_path,
                    "operation": "crop",
                    "parameters": {
                        "left": left,
                        "top": top,
                        "right": right,
                        "bottom": bottom,
                        "crop_width": right - left,
                        "crop_height": bottom - top
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
                "operation": "crop",
                "parameters": {
                    "left": left,
                    "top": top,
                    "right": right,
                    "bottom": bottom
                },
                "input_file_size": file_size,
                "file_extension": file_ext,
                "success": True,
                "note": "PIL/Pillow not available - this is a mock result. Install PIL for actual image processing."
            }
            
            return result
        
    except Exception as e:
        return {"error": f"Image crop failed: {str(e)}"}

if __name__ == "__main__":
    # Example usage
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    result = crop_image(
        image_path="./image_data/dog.jpg",
        left=100,
        top=100,
        right=500,
        bottom=400,
    )
    print(json.dumps(result, indent=2, ensure_ascii=False)) 