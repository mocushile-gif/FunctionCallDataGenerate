import os
import json
from typing import Dict, Any, Optional, List, Tuple
from dotenv import load_dotenv
load_dotenv()

def extract_image_colors(image_path: str, num_colors: int = 5, output_path: Optional[str] = None):
    """
    Extract dominant colors from an image.

    Parameters:
    - image_path (str): Path to the input image file.
    - num_colors (int): Number of dominant colors to extract (1-20).
    - output_path (str, optional): Path for the output color palette image. If not provided, will create auto-named file.

    Returns:
    - dict: Processing result information including color data.
    """
    
    try:
        # Check if input file exists
        if not os.path.exists(image_path):
            return {"error": f"Input image file not found: {image_path}"}
        
        # Validate parameters
        if num_colors < 1 or num_colors > 20:
            return {"error": "num_colors must be between 1 and 20"}
        
        # Set output path if not provided
        if output_path is None:
            base_name = os.path.splitext(image_path)[0]
            output_path = f"{base_name}_colors.png"
        
        # Get file information
        file_size = os.path.getsize(image_path)
        
        # Check if PIL is available for actual image processing
        try:
            from PIL import Image
            import numpy as np
            from collections import Counter
            
            # Open the image
            with Image.open(image_path) as img:
                original_size = img.size
                original_mode = img.mode
                
                # Convert to RGB if necessary
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Resize image for faster processing
                img_small = img.resize((150, 150))
                
                # Get all pixels
                pixels = list(img_small.getdata())
                
                # Count color occurrences
                color_counts = Counter(pixels)
                
                # Get most common colors
                most_common_colors = color_counts.most_common(num_colors)
                
                # Extract color information
                colors_data = []
                for i, (color, count) in enumerate(most_common_colors):
                    r, g, b = color
                    hex_color = f"#{r:02x}{g:02x}{b:02x}"
                    percentage = (count / len(pixels)) * 100
                    
                    colors_data.append({
                        "rank": i + 1,
                        "rgb": (r, g, b),
                        "hex": hex_color,
                        "percentage": round(percentage, 2),
                        "count": count
                    })
                
                # Create color palette image
                palette_width = 200
                palette_height = 50
                palette_img = Image.new('RGB', (palette_width, palette_height), 'white')
                
                # Draw color swatches
                swatch_width = palette_width // num_colors
                for i, color_data in enumerate(colors_data):
                    x1 = i * swatch_width
                    x2 = (i + 1) * swatch_width if i < num_colors - 1 else palette_width
                    color = color_data['rgb']
                    
                    # Create a rectangle for this color
                    for x in range(x1, x2):
                        for y in range(palette_height):
                            palette_img.putpixel((x, y), color)
                
                # Save the palette image
                palette_img.save(output_path)
                
                # Get output file information
                output_size = os.path.getsize(output_path)
                
                result = {
                    "input_path": image_path,
                    "output_path": output_path,
                    "operation": "extract_colors",
                    "parameters": {
                        "num_colors": num_colors
                    },
                    "original_size": original_size,
                    "original_mode": original_mode,
                    "input_file_size": file_size,
                    "output_file_size": output_size,
                    "colors": colors_data,
                    "success": True
                }
                
                return result
                
        except ImportError:
            return {"error": "PIL (Pillow) and numpy libraries are required for image processing"}
            
    except Exception as e:
        return {"error": f"Error processing image: {str(e)}"}

if __name__ == "__main__":
    # Example usage
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    result = extract_image_colors("./image_data/dog.jpg", num_colors=5)
    print(json.dumps(result, indent=2)) 