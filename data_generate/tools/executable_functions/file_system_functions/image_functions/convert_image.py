import os
import json
from typing import Dict, Any, Optional
from dotenv import load_dotenv
load_dotenv()

def convert_image(image_path: str, mode: str, output_path: Optional[str] = None):
    """
    Convert image to different color mode.

    Parameters:
    - image_path (str): Path to the input image file.
    - mode (str): Target color mode (RGB, RGBA, L, P, CMYK, YCbCr, LAB, HSV, I, F).
    - output_path (str, optional): Path for the output image. If not provided, will create auto-named file.

    Returns:
    - dict: Processing result information.
    """
    
    
    try:
        # Check if input file exists
        if not os.path.exists(image_path):
            return {"error": f"Input image file not found: {image_path}"}
        
        # Validate mode
        valid_modes = ["RGB", "RGBA", "L", "P", "CMYK", "YCbCr", "LAB", "HSV", "I", "F"]
        if mode not in valid_modes:
            return {"error": f"Invalid mode. Must be one of: {valid_modes}"}
        
        # Set output path if not provided
        if output_path is None:
            base_name = os.path.splitext(image_path)[0]
            ext = os.path.splitext(image_path)[1]
            output_path = f"{base_name}_{mode.lower()}{ext}"
        
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
                
                # Convert the image
                img = img.convert(mode)
                
                # Save the processed image
                img.save(output_path)
                
                # Get output file information
                output_size = os.path.getsize(output_path)
                
                result = {
                    "input_path": image_path,
                    "output_path": output_path,
                    "operation": "convert",
                    "parameters": {
                        "mode": mode
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
                "operation": "convert",
                "parameters": {
                    "mode": mode
                },
                "input_file_size": file_size,
                "file_extension": file_ext,
                "success": True,
                "note": "PIL/Pillow not available - this is a mock result. Install PIL for actual image processing."
            }
            
            return result
        
    except Exception as e:
        return {"error": f"Image convert failed: {str(e)}"}

if __name__ == "__main__":
    # Example usage
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    result = convert_image(
        image_path="./image_data/dog.jpg",
        mode="L",
    )
    print(json.dumps(result, indent=2, ensure_ascii=False)) 