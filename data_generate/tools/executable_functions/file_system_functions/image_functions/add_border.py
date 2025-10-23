import os
import json
from PIL import Image, ImageDraw
from dotenv import load_dotenv
load_dotenv()

def add_border(image_path, border_width=20, border_color=(255, 255, 255), border_style="solid", 
               output_path=None, border_position="all"):
    """
    Add border to an image.
    
    Args:
        image_path (str): Path to the input image file
        border_width (int): Width of the border in pixels
        border_color (tuple): Border color (R, G, B)
        border_style (str): Border style - "solid", "dashed", "dotted", "double"
        output_path (str): Path for the output image
        border_position (str): Border position - "all", "top", "bottom", "left", "right"
    
    Returns:
        dict: Result information including success status and output path
    """
    
    
    try:
        # Validate input file
        if not os.path.exists(image_path):
            return {
                "success": False,
                "error": f"Input image file not found: {image_path}"
            }
        
        # Open image
        with Image.open(image_path) as img:
            # Convert to RGB if necessary
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Calculate new dimensions
            original_width, original_height = img.size
            
            if border_position == "all":
                new_width = original_width + 2 * border_width
                new_height = original_height + 2 * border_width
                border_left = border_top = border_width
            elif border_position == "top":
                new_width = original_width
                new_height = original_height + border_width
                border_left = 0
                border_top = border_width
            elif border_position == "bottom":
                new_width = original_width
                new_height = original_height + border_width
                border_left = 0
                border_top = 0
            elif border_position == "left":
                new_width = original_width + border_width
                new_height = original_height
                border_left = border_width
                border_top = 0
            elif border_position == "right":
                new_width = original_width + border_width
                new_height = original_height
                border_left = 0
                border_top = 0
            else:
                return {
                    "success": False,
                    "error": f"Unsupported border position: {border_position}"
                }
            

            if type(border_color) is list:
                border_color=tuple(border_color)
            # Create new image with border
            new_img = Image.new('RGB', (new_width, new_height), border_color)
            
            # Paste original image
            new_img.paste(img, (border_left, border_top))
            
            # Add border effects if needed
            if border_style in ["dashed", "dotted", "double"]:
                draw = ImageDraw.Draw(new_img)
                
                if border_style == "dashed":
                    # Create dashed border
                    dash_length = 10
                    gap_length = 5
                    
                    # Top border
                    if border_position in ["all", "top"]:
                        for x in range(0, new_width, dash_length + gap_length):
                            draw.line([(x, 0), (min(x + dash_length, new_width), 0)], 
                                    fill=border_color, width=border_width)
                    
                    # Bottom border
                    if border_position in ["all", "bottom"]:
                        for x in range(0, new_width, dash_length + gap_length):
                            draw.line([(x, new_height - border_width), 
                                     (min(x + dash_length, new_width), new_height - border_width)], 
                                    fill=border_color, width=border_width)
                    
                    # Left border
                    if border_position in ["all", "left"]:
                        for y in range(0, new_height, dash_length + gap_length):
                            draw.line([(0, y), (0, min(y + dash_length, new_height))], 
                                    fill=border_color, width=border_width)
                    
                    # Right border
                    if border_position in ["all", "right"]:
                        for y in range(0, new_height, dash_length + gap_length):
                            draw.line([(new_width - border_width, y), 
                                     (new_width - border_width, min(y + dash_length, new_height))], 
                                    fill=border_color, width=border_width)
                
                elif border_style == "dotted":
                    # Create dotted border
                    dot_spacing = 15
                    
                    # Top border
                    if border_position in ["all", "top"]:
                        for x in range(border_width//2, new_width - border_width//2, dot_spacing):
                            draw.ellipse([(x - 2, border_width//2 - 2), 
                                        (x + 2, border_width//2 + 2)], fill=border_color)
                    
                    # Bottom border
                    if border_position in ["all", "bottom"]:
                        for x in range(border_width//2, new_width - border_width//2, dot_spacing):
                            draw.ellipse([(x - 2, new_height - border_width//2 - 2), 
                                        (x + 2, new_height - border_width//2 + 2)], fill=border_color)
                    
                    # Left border
                    if border_position in ["all", "left"]:
                        for y in range(border_width//2, new_height - border_width//2, dot_spacing):
                            draw.ellipse([(border_width//2 - 2, y - 2), 
                                        (border_width//2 + 2, y + 2)], fill=border_color)
                    
                    # Right border
                    if border_position in ["all", "right"]:
                        for y in range(border_width//2, new_height - border_width//2, dot_spacing):
                            draw.ellipse([(new_width - border_width//2 - 2, y - 2), 
                                        (new_width - border_width//2 + 2, y + 2)], fill=border_color)
                
                elif border_style == "double":
                    # Create double border
                    inner_border = border_width // 3
                    outer_border = border_width - inner_border
                    
                    # Create inner border
                    inner_img = Image.new('RGB', (new_width - 2*outer_border, new_height - 2*outer_border), border_color)
                    inner_img.paste(img, (inner_border, inner_border))
                    
                    # Create outer border
                    outer_img = Image.new('RGB', (new_width, new_height), border_color)
                    outer_img.paste(inner_img, (outer_border, outer_border))
                    new_img = outer_img
            
            # Determine output path
            if output_path is None:
                base_name = os.path.splitext(image_path)[0]
                ext = os.path.splitext(image_path)[1]
                output_path = f"{base_name}_bordered{ext}"
            
            # Save image
            new_img.save(output_path, quality=95)
            
            return {
                "success": True,
                "output_path": output_path,
                "border_width": border_width,
                "border_color": border_color,
                "border_style": border_style,
                "border_position": border_position,
                "original_size": f"{original_width}x{original_height}",
                "new_size": f"{new_width}x{new_height}"
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": f"Error adding border: {str(e)}"
        }

if __name__ == "__main__":
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    # Test the function
    result = add_border(
        image_path="./image_data/dog.jpg",
        border_width=20,
        border_color=[255, 0, 0],
        border_style="solid",
        border_position="all"
    )
    print(json.dumps(result, indent=2)) 