import os
import json
from typing import Dict, Any, Optional, Tuple
from dotenv import load_dotenv
load_dotenv()

def add_text_to_image(image_path: str, text: str, position: Tuple[int, int] = (10, 10),
                      font_size: int = 24, font_color: str = "white", 
                      font_name: str = "arial.ttf", background_color: Optional[str] = None,
                      output_path: Optional[str] = None):
    """
    Add text to an image.

    Parameters:
    - image_path (str): Path to the input image file.
    - text (str): Text to add to the image.
    - position (tuple): Position (x, y) where to place the text.
    - font_size (int): Font size in pixels (8-72).
    - font_color (str): Font color (hex color or color name).
    - font_name (str): Font name or path to font file.
    - background_color (str, optional): Background color for text box (hex color or color name).
    - output_path (str, optional): Path for the output image. If not provided, will create auto-named file.

    Returns:
    - dict: Processing result information.
    """
    
    
    try:
        # Check if input file exists
        if not os.path.exists(image_path):
            return {"error": f"Input image file not found: {image_path}"}
        
        # Validate parameters
        if not text or len(text.strip()) == 0:
            return {"error": "Text cannot be empty"}
        
        if font_size < 8 or font_size > 72:
            return {"error": "font_size must be between 8 and 72"}
        
        if len(position) != 2:
            return {"error": "position must be a tuple of 2 integers (x, y)"}
        
        # Set output path if not provided
        if output_path is None:
            base_name = os.path.splitext(image_path)[0]
            ext = os.path.splitext(image_path)[1]
            output_path = f"{base_name}_with_text{ext}"
        
        # Get file information
        file_size = os.path.getsize(image_path)
        
        # Check if PIL is available for actual image processing
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            # Open the image
            with Image.open(image_path) as img:
                original_size = img.size
                original_mode = img.mode
                
                # Convert to RGB if necessary
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Create a copy for drawing
                img_with_text = img.copy()
                draw = ImageDraw.Draw(img_with_text)
                
                # Try to load font
                try:
                    # Try to use system font
                    font = ImageFont.truetype(font_name, font_size)
                except:
                    try:
                        # Try default font
                        font = ImageFont.load_default()
                    except:
                        # Use basic font
                        font = ImageFont.load_default()
                
                # Get text bounding box
                bbox = draw.textbbox(position, text, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                
                # Add background if specified
                if background_color:
                    # Create background rectangle
                    bg_bbox = (
                        position[0] - 5,
                        position[1] - 5,
                        position[0] + text_width + 5,
                        position[1] + text_height + 5
                    )
                    draw.rectangle(bg_bbox, fill=background_color)
                
                # Add text
                draw.text(position, text, fill=font_color, font=font)
                
                # Save the processed image
                img_with_text.save(output_path)
                
                # Get output file information
                output_size = os.path.getsize(output_path)
                
                result = {
                    "input_path": image_path,
                    "output_path": output_path,
                    "operation": "add_text_to_image",
                    "parameters": {
                        "text": text,
                        "position": position,
                        "font_size": font_size,
                        "font_color": font_color,
                        "font_name": font_name,
                        "background_color": background_color
                    },
                    "text_info": {
                        "text_width": text_width,
                        "text_height": text_height,
                        "text_length": len(text)
                    },
                    "original_size": original_size,
                    "processed_size": img_with_text.size,
                    "original_mode": original_mode,
                    "processed_mode": img_with_text.mode,
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
    result = add_text_to_image("./image_data/dog.jpg", "Hello World!", position=(50, 50), 
                              font_size=32, font_color="red", background_color="yellow")
    print(json.dumps(result, indent=2)) 