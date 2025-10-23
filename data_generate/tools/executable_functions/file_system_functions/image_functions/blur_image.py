import os
import json
from typing import Dict, Any, Optional
from dotenv import load_dotenv
load_dotenv()

def blur_image(image_path: str, blur_type: str = "gaussian", radius: float = 5.0,
               output_path: Optional[str] = None):
    """
    Apply blur effect to an image.

    Parameters:
    - image_path (str): Path to the input image file.
    - blur_type (str): Type of blur effect. Options: "gaussian", "box", "motion".
    - radius (float): Blur radius/intensity (1.0-20.0).
    - output_path (str, optional): Path for the output image. If not provided, will create auto-named file.

    Returns:
    - dict: Processing result information.
    """
    
    try:
        # Check if input file exists
        if not os.path.exists(image_path):
            return {"error": f"Input image file not found: {image_path}"}
        
        # Validate parameters
        if blur_type not in ["gaussian", "box", "motion"]:
            return {"error": "blur_type must be one of: gaussian, box, motion"}
        
        if radius < 0.1 or radius > 50.0:
            return {"error": "radius must be between 0.1 and 50.0"}
        
        # Set output path if not provided
        if output_path is None:
            base_name = os.path.splitext(image_path)[0]
            ext = os.path.splitext(image_path)[1]
            output_path = f"{base_name}_blurred_{blur_type}{ext}"
        
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
                
                # Apply blur effect
                if blur_type == "gaussian":
                    blurred_img = img.filter(ImageFilter.GaussianBlur(radius=radius))
                elif blur_type == "box":
                    blurred_img = img.filter(ImageFilter.BoxBlur(radius=int(radius)))
                elif blur_type == "motion":
                    # Create motion blur effect
                    blurred_img = img.filter(ImageFilter.GaussianBlur(radius=radius/2))
                
                # Save the processed image
                blurred_img.save(output_path)
                
                # Get output file information
                output_size = os.path.getsize(output_path)
                
                result = {
                    "input_path": image_path,
                    "output_path": output_path,
                    "operation": "blur",
                    "parameters": {
                        "blur_type": blur_type,
                        "radius": radius
                    },
                    "original_size": original_size,
                    "processed_size": blurred_img.size,
                    "original_mode": original_mode,
                    "processed_mode": blurred_img.mode,
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
    result = blur_image("./image_data/dog.jpg", blur_type="gaussian", radius=3.0)
    print(json.dumps(result, indent=2)) 