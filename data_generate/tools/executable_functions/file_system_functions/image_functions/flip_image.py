import os
import json
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from PIL import Image
load_dotenv()

def flip_image(image_path: str, direction: str = "horizontal",
               output_path: Optional[str] = None):
    """
    Flip image horizontally or vertically.

    Parameters:
    - image_path (str): Path to the input image file.
    - direction (str): Flip direction ("horizontal" or "vertical").
    - output_path (str, optional): Path for the output image. If not provided, will create auto-named file.

    Returns:
    - dict: Processing result information.
    """
    
    
    try:
        # Check if input file exists
        if not os.path.exists(image_path):
            return {"error": f"Input image file not found: {image_path}"}
        
        # Validate direction
        if direction not in ["horizontal", "vertical"]:
            return {"error": "Direction must be 'horizontal' or 'vertical'"}
        
        # Set output path if not provided
        if output_path is None:
            base_name = os.path.splitext(image_path)[0]
            ext = os.path.splitext(image_path)[1]
            output_path = f"{base_name}_flipped_{direction}{ext}"
        
        # Get file information
        file_size = os.path.getsize(image_path)
        file_ext = os.path.splitext(image_path)[1].lower()
        
        # Check if PIL is available for actual image processing
        try:
            
            
            # Open the image
            with Image.open(image_path) as img:
                original_size = img.size
                original_mode = img.mode
                
                # Flip the image
                if direction == "horizontal":
                    img = img.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
                elif direction == "vertical":
                    img = img.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
                
                # Save the processed image
                img.save(output_path)
                
                # Get output file information
                output_size = os.path.getsize(output_path)
                
                result = {
                    "input_path": image_path,
                    "output_path": output_path,
                    "operation": "flip",
                    "parameters": {
                        "direction": direction
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
                "operation": "flip",
                "parameters": {
                    "direction": direction
                },
                "input_file_size": file_size,
                "file_extension": file_ext,
                "success": True,
                "note": "PIL/Pillow not available - this is a mock result. Install PIL for actual image processing."
            }
            
            return result
        
    except Exception as e:
        return {"error": f"Image flip failed: {str(e)}"}

if __name__ == "__main__":
    # Example usage
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    result = flip_image(
        image_path="./image_data/dog.jpg",
        direction="horizontal",
    )
    print(json.dumps(result, indent=2, ensure_ascii=False)) 