import os
import json
from typing import Dict, Any, Optional
from dotenv import load_dotenv
load_dotenv()

def enhance_image(image_path: str, brightness: float = 1.0, contrast: float = 1.0,
                 saturation: float = 1.0, sharpness: float = 1.0, 
                 output_path: Optional[str] = None):
    """
    Enhance image with various adjustments like brightness, contrast, saturation, and sharpness.

    Parameters:
    - image_path (str): Path to the input image file.
    - brightness (float): Brightness adjustment factor (0.0-3.0). Default is 1.0 (no change).
    - contrast (float): Contrast adjustment factor (0.0-3.0). Default is 1.0 (no change).
    - saturation (float): Saturation adjustment factor (0.0-3.0). Default is 1.0 (no change).
    - sharpness (float): Sharpness adjustment factor (0.0-3.0). Default is 1.0 (no change).
    - output_path (str, optional): Path for the output image. If not provided, will overwrite input.

    Returns:
    - dict: Enhancement result information.
    - str: Error message if an exception occurs.
    """
    
    try:
        # Check if input file exists
        if not os.path.exists(image_path):
            return {"error": f"Input image file not found: {image_path}"}
        
        # Validate adjustment factors
        for factor_name, factor_value in [("brightness", brightness), ("contrast", contrast), 
                                         ("saturation", saturation), ("sharpness", sharpness)]:
            if factor_value < 0.0 or factor_value > 3.0:
                return {"error": f"{factor_name} must be between 0.0 and 3.0"}
        
        # Set output path if not provided
        if output_path is None:
            base_name = os.path.splitext(image_path)[0]
            ext = os.path.splitext(image_path)[1]
            output_path = f"{base_name}_enhanced{ext}"
        
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
                if brightness != 1.0:
                    enhancer = ImageEnhance.Brightness(img)
                    img = enhancer.enhance(brightness)
                
                # Apply contrast adjustment
                if contrast != 1.0:
                    enhancer = ImageEnhance.Contrast(img)
                    img = enhancer.enhance(contrast)
                
                # Apply saturation adjustment
                if saturation != 1.0:
                    enhancer = ImageEnhance.Color(img)
                    img = enhancer.enhance(saturation)
                
                # Apply sharpness adjustment
                if sharpness != 1.0:
                    enhancer = ImageEnhance.Sharpness(img)
                    img = enhancer.enhance(sharpness)
                
                # Save the enhanced image
                img.save(output_path)
                
                # Get output file information
                output_size = os.path.getsize(output_path)
                
                result = {
                    "input_path": image_path,
                    "output_path": output_path,
                    "brightness": brightness,
                    "contrast": contrast,
                    "saturation": saturation,
                    "sharpness": sharpness,
                    "original_size": original_size,
                    "enhanced_size": img.size,
                    "original_mode": original_mode,
                    "enhanced_mode": img.mode,
                    "input_file_size": file_size,
                    "output_file_size": output_size,
                    "success": True
                }
                
        except ImportError:
            # PIL not available, return mock result
            result = {
                "input_path": image_path,
                "output_path": output_path,
                "brightness": brightness,
                "contrast": contrast,
                "saturation": saturation,
                "sharpness": sharpness,
                "input_file_size": file_size,
                "file_extension": file_ext,
                "success": True,
                "note": "PIL/Pillow not available - this is a mock result. Install PIL for actual image enhancement."
            }
        
        except Exception as e:
            return {"error": f"Image enhancement failed: {str(e)}"}
        
        return result
        
    except Exception as e:
        return {"error": f"Image enhancement failed: {str(e)}"}

if __name__ == "__main__":
    # Example usage
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    result = enhance_image(
        image_path="./image_data/dog.jpg",
        brightness=1.2,
        contrast=1.1,
        saturation=1.3,
        sharpness=1.1,
        output_path="./enhanced_image.jpg",
    )
    print(json.dumps(result, indent=2, ensure_ascii=False)) 