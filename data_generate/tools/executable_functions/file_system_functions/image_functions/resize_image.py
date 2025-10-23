import os
import json
from typing import Dict, Any, Optional
from dotenv import load_dotenv
load_dotenv()

def resize_image(image_path: str, width: Optional[int] = None, height: Optional[int] = None,
                 output_path: Optional[str] = None):
    """
    Resize image to specified dimensions.

    Parameters:
    - image_path (str): Path to the input image file.
    - width (int, optional): New width in pixels. If not provided, maintains aspect ratio.
    - height (int, optional): New height in pixels. If not provided, maintains aspect ratio.
    - output_path (str, optional): Path for the output image. If not provided, will create auto-named file.

    Returns:
    - dict: Processing result information.
    """
    
    try:
        # Check if input file exists
        if not os.path.exists(image_path):
            return {"error": f"Input image file not found: {image_path}"}
        
        # Validate dimensions
        if width is not None and width <= 0:
            return {"error": "Width must be greater than 0"}
        if height is not None and height <= 0:
            return {"error": "Height must be greater than 0"}
        if width is None and height is None:
            return {"error": "At least one of width or height must be specified"}
        
        # Set output path if not provided
        if output_path is None:
            base_name = os.path.splitext(image_path)[0]
            ext = os.path.splitext(image_path)[1]
            output_path = f"{base_name}_resized{ext}"
        
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
                
                # Calculate new dimensions
                if width is not None and height is not None:
                    new_size = (width, height)
                elif width is not None:
                    # Maintain aspect ratio
                    ratio = width / img.width
                    new_height = int(img.height * ratio)
                    new_size = (width, new_height)
                else:  # height is not None
                    # Maintain aspect ratio
                    ratio = height / img.height
                    new_width = int(img.width * ratio)
                    new_size = (new_width, height)
                
                # Resize the image
                img = img.resize(new_size, Image.Resampling.LANCZOS)
                
                # Save the processed image
                img.save(output_path)
                
                # Get output file information
                output_size = os.path.getsize(output_path)
                
                result = {
                    "input_path": image_path,
                    "output_path": output_path,
                    "operation": "resize",
                    "parameters": {
                        "width": width,
                        "height": height,
                        "new_width": new_size[0],
                        "new_height": new_size[1]
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
                "operation": "resize",
                "parameters": {
                    "width": width,
                    "height": height
                },
                "input_file_size": file_size,
                "file_extension": file_ext,
                "success": True,
                "note": "PIL/Pillow not available - this is a mock result. Install PIL for actual image processing."
            }
            return result
        
    except Exception as e:
        return {"error": f"Image resize failed: {str(e)}"}

if __name__ == "__main__":
    # Example usage
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    result = resize_image(
        image_path="./image_data/dog.jpg",
        width=800,
        height=600,
        output_path="./image_data/resize_dog.png"
    )
    print(json.dumps(result, indent=2, ensure_ascii=False)) 