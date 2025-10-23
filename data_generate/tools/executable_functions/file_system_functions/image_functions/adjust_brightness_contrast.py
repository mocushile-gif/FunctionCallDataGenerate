import os
import json
from typing import Dict, Any, Optional
from dotenv import load_dotenv
load_dotenv()

def adjust_brightness_contrast(image_path: str, brightness_factor: float = 1.0, contrast_factor: float = 1.0,
                              output_path: Optional[str] = None):
    """
    Adjust brightness and contrast of an image.

    Parameters:
    - image_path (str): Path to the input image file.
    - brightness_factor (float): Brightness adjustment factor (0.1-3.0, 1.0 = no change).
    - contrast_factor (float): Contrast adjustment factor (0.1-3.0, 1.0 = no change).
    - output_path (str, optional): Path for the output image. If not provided, will create auto-named file.

    Returns:
    - dict: Processing result information.
    """
    
    try:
        # Check if input file exists
        if not os.path.exists(image_path):
            return {"error": f"Input image file not found: {image_path}"}
        
        # Validate parameters
        if brightness_factor < 0.1 or brightness_factor > 5.0:
            return {"error": "brightness_factor must be between 0.1 and 5.0"}
        
        if contrast_factor < 0.1 or contrast_factor > 5.0:
            return {"error": "contrast_factor must be between 0.1 and 5.0"}
        
        # Set output path if not provided
        if output_path is None:
            base_name = os.path.splitext(image_path)[0]
            ext = os.path.splitext(image_path)[1]
            output_path = f"{base_name}_adjusted{ext}"
        
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
                
                # Apply brightness adjustment
                brightness_enhancer = ImageEnhance.Brightness(img)
                adjusted_img = brightness_enhancer.enhance(brightness_factor)
                
                # Apply contrast adjustment
                contrast_enhancer = ImageEnhance.Contrast(adjusted_img)
                final_img = contrast_enhancer.enhance(contrast_factor)
                
                # Save the processed image
                final_img.save(output_path)
                
                # Get output file information
                output_size = os.path.getsize(output_path)
                
                result = {
                    "input_path": image_path,
                    "output_path": output_path,
                    "operation": "adjust_brightness_contrast",
                    "parameters": {
                        "brightness_factor": brightness_factor,
                        "contrast_factor": contrast_factor
                    },
                    "original_size": original_size,
                    "processed_size": final_img.size,
                    "original_mode": original_mode,
                    "processed_mode": final_img.mode,
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
    result = adjust_brightness_contrast("./image_data/dog.jpg", brightness_factor=1.2, contrast_factor=1.1)
    print(json.dumps(result, indent=2)) 