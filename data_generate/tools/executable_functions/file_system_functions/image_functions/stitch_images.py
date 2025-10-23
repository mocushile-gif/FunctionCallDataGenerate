import os
import json
import time
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv
load_dotenv()

def stitch_images(image_paths: List[str], direction: str = "horizontal", 
                 background_color: str = "white", spacing: int = 0,
                 output_path: Optional[str] = None):
    """
    Stitch multiple images together horizontally or vertically.

    Parameters:
    - image_paths (list): List of paths to input image files.
    - direction (str): Direction to stitch images ("horizontal" or "vertical").
    - background_color (str): Background color for the stitched image.
    - spacing (int): Spacing between images in pixels. Default is 0.
    - output_path (str, optional): Path for the output image. If not provided, will create stitched version.

    Returns:
    - dict: Stitching result information.
    - str: Error message if an exception occurs.
    """
    
    try:
        # Validate input
        if not image_paths:
            return {"error": "No image paths provided"}
        
        if len(image_paths) < 2:
            return {"error": "At least 2 images are required for stitching"}
        
        # Validate direction
        if direction not in ["horizontal", "vertical"]:
            return {"error": "Direction must be 'horizontal' or 'vertical'"}
        
        # Validate spacing
        if spacing < 0:
            return {"error": "Spacing must be non-negative"}
        
        # Check if all input files exist
        for image_path in image_paths:
            if not os.path.exists(image_path):
                return {"error": f"Input image file not found: {image_path}"}
        
        # Set output path if not provided
        if output_path is None:
            timestamp = int(time.time())
            output_path = f"./stitched_images/stitched_{direction}_{timestamp}.png"
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Check if PIL is available for actual image processing
        try:
            from PIL import Image
            
            # Load all images
            images = []
            image_info = []
            
            for image_path in image_paths:
                with Image.open(image_path) as img:
                    # Convert to RGB if needed
                    if img.mode != 'RGB':
                        img = img.convert('RGB')
                    
                    images.append(img.copy())
                    image_info.append({
                        "path": image_path,
                        "size": img.size,
                        "mode": img.mode,
                        "file_size": os.path.getsize(image_path)
                    })
            
            # Calculate dimensions for stitched image
            if direction == "horizontal":
                # Calculate total width and max height
                total_width = sum(img.width for img in images) + spacing * (len(images) - 1)
                max_height = max(img.height for img in images)
                
                # Create new image
                stitched_img = Image.new('RGB', (total_width, max_height), background_color)
                
                # Paste images horizontally
                x_offset = 0
                for img in images:
                    # Center vertically
                    y_offset = (max_height - img.height) // 2
                    stitched_img.paste(img, (x_offset, y_offset))
                    x_offset += img.width + spacing
                
            else:  # vertical
                # Calculate max width and total height
                max_width = max(img.width for img in images)
                total_height = sum(img.height for img in images) + spacing * (len(images) - 1)
                
                # Create new image
                stitched_img = Image.new('RGB', (max_width, total_height), background_color)
                
                # Paste images vertically
                y_offset = 0
                for img in images:
                    # Center horizontally
                    x_offset = (max_width - img.width) // 2
                    stitched_img.paste(img, (x_offset, y_offset))
                    y_offset += img.height + spacing
            
            # Save the stitched image
            stitched_img.save(output_path)
            
            # Get output file information
            output_size = os.path.getsize(output_path)
            
            result = {
                "input_paths": image_paths,
                "output_path": output_path,
                "direction": direction,
                "background_color": background_color,
                "spacing": spacing,
                "num_images": len(images),
                "stitched_size": stitched_img.size,
                "stitched_mode": stitched_img.mode,
                "output_file_size": output_size,
                "image_info": image_info,
                "success": True
            }
            
        except ImportError:
            # PIL not available, return mock result
            result = {
                "input_paths": image_paths,
                "output_path": output_path,
                "direction": direction,
                "background_color": background_color,
                "spacing": spacing,
                "num_images": len(image_paths),
                "success": True,
                "note": "PIL/Pillow not available - this is a mock result. Install PIL for actual image stitching."
            }
        
        except Exception as e:
            return {"error": f"Image stitching failed: {str(e)}"}
        
        return result
        
    except Exception as e:
        return {"error": f"Image stitching failed: {str(e)}"}

if __name__ == "__main__":
    # Example usage
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    result = stitch_images(
        image_paths=["./image_data/dog.jpg", "./image_data/cat.gif"],
        direction="horizontal",
        background_color="white",
        spacing=10,
        output_path="./stitched_image.png",
    )
    print(json.dumps(result, indent=2, ensure_ascii=False)) 