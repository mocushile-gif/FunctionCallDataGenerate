import os
import json
from typing import Dict, Any, Optional
from dotenv import load_dotenv
load_dotenv()

def sharpen_image(image_path: str, factor: float = 1.5, threshold: float = 0.0,
                  output_path: Optional[str] = None):
    """
    Apply sharpening effect to an image.

    Parameters:
    - image_path (str): Path to the input image file.
    - factor (float): Sharpening factor (0.1-3.0).
    - threshold (float): Threshold for sharpening (0.0-1.0).
    - output_path (str, optional): Path for the output image. If not provided, will create auto-named file.

    Returns:
    - dict: Processing result information.
    """
    
    try:
        # Check if input file exists
        if not os.path.exists(image_path):
            return {"error": f"Input image file not found: {image_path}"}
        
        # Validate parameters
        if factor < 0.1 or factor > 5.0:
            return {"error": "factor must be between 0.1 and 5.0"}
        
        if threshold < 0.0 or threshold > 1.0:
            return {"error": "threshold must be between 0.0 and 1.0"}
        
        # Set output path if not provided
        if output_path is None:
            base_name = os.path.splitext(image_path)[0]
            ext = os.path.splitext(image_path)[1]
            output_path = f"{base_name}_sharpened{ext}"
        
        # Get file information
        file_size = os.path.getsize(image_path)
        file_ext = os.path.splitext(image_path)[1].lower()
        
        # Check if PIL is available for actual image processing
        try:
            from PIL import Image, ImageEnhance
            
            # Open the image
            with Image.open(image_path) as img:
                original_size = img.size
                original_mode = img.mode
                
                # Apply sharpening effect
                enhancer = ImageEnhance.Sharpness(img)
                sharpened_img = enhancer.enhance(factor)
                
                # Save the processed image
                sharpened_img.save(output_path)
                
                # Get output file information
                output_size = os.path.getsize(output_path)
                
                result = {
                    "input_path": image_path,
                    "output_path": output_path,
                    "operation": "sharpen",
                    "parameters": {
                        "factor": factor,
                        "threshold": threshold
                    },
                    "original_size": original_size,
                    "processed_size": sharpened_img.size,
                    "original_mode": original_mode,
                    "processed_mode": sharpened_img.mode,
                    "input_file_size": file_size,
                    "output_file_size": output_size,
                    "success": True
                }
                
                return result
                
        except ImportError:
            return {"error": "PIL (Pillow) library is required for image processing"}
            
    except Exception as e:
        return {"error": f"Error processing image: {str(e)}"}

if __name__ == "__main__":
    # Example usage
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    result = sharpen_image("./image_data/dog.jpg", factor=1.5, threshold=0.0)
    print(json.dumps(result, indent=2)) 