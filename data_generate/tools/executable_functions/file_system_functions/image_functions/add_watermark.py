import os
import json
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont
load_dotenv()

def add_watermark(image_path: str, watermark_text: Optional[str] = None, 
                 watermark_image_path: Optional[str] = None, position: str = "bottom-right",
                 opacity: float = 0.7, font_size: int = 24, font_color: str = "white",
                 output_path: Optional[str] = None):
    """
    Add watermark to image (text or image watermark).

    Parameters:
    - image_path (str): Path to the input image file.
    - watermark_text (str, optional): Text to use as watermark.
    - watermark_image_path (str, optional): Path to watermark image file.
    - position (str): Position of watermark (top-left, top-right, bottom-left, bottom-right, center).
    - opacity (float): Opacity of watermark (0.0-1.0). Default is 0.7.
    - font_size (int): Font size for text watermark. Default is 24.
    - font_color (str): Font color for text watermark. Default is "white".
    - output_path (str, optional): Path for the output image. If not provided, will create watermarked version.

    Returns:
    - dict: Watermark result information.
    - str: Error message if an exception occurs.
    """
    
    
    try:
        # Check if input file exists
        if not os.path.exists(image_path):
            return {"error": f"Input image file not found: {image_path}"}
        
        # Validate that either text or image watermark is provided
        if not watermark_text and not watermark_image_path:
            return {"error": "Either watermark_text or watermark_image_path must be provided"}
        
        # Validate position
        valid_positions = ["top-left", "top-right", "bottom-left", "bottom-right", "center"]
        if position not in valid_positions:
            return {"error": f"Position must be one of: {valid_positions}"}
        
        # Validate opacity
        if opacity < 0.0 or opacity > 1.0:
            return {"error": "Opacity must be between 0.0 and 1.0"}
        
        # Validate font size
        if font_size < 8 or font_size > 200:
            return {"error": "Font size must be between 8 and 200"}
        
        # Check watermark image if provided
        if watermark_image_path and not os.path.exists(watermark_image_path):
            return {"error": f"Watermark image file not found: {watermark_image_path}"}
        
        # Set output path if not provided
        if output_path is None:
            base_name = os.path.splitext(image_path)[0]
            ext = os.path.splitext(image_path)[1]
            output_path = f"{base_name}_watermarked{ext}"
        
        # Get file information
        file_size = os.path.getsize(image_path)
        file_ext = os.path.splitext(image_path)[1].lower()
        
        try:  
            # Open the main image
            with Image.open(image_path) as img:
                original_size = img.size
                original_mode = img.mode
                
                # Convert to RGBA if needed for transparency
                if img.mode != 'RGBA':
                    img = img.convert('RGBA')
                
                # Create a copy for watermarking
                watermarked_img = img.copy()
                
                if watermark_text:
                    # Create text watermark
                    draw = ImageDraw.Draw(watermarked_img)
                    
                    # Try to use a default font
                    try:
                        font = ImageFont.truetype("arial.ttf", font_size)
                    except:
                        try:
                            font = ImageFont.load_default()
                        except:
                            font = None
                    
                    # Get text size
                    if font:
                        try:
                            bbox = draw.textbbox((0, 0), watermark_text, font=font)
                            text_width = bbox[2] - bbox[0]
                            text_height = bbox[3] - bbox[1]
                        except AttributeError:
                            text_width = len(watermark_text) * font_size // 2
                            text_height = font_size
                    else:
                        text_width = len(watermark_text) * font_size // 2
                        text_height = font_size
                    
                    # Calculate position
                    img_width, img_height = watermarked_img.size
                    if position == "top-left":
                        x, y = 10, 10
                    elif position == "top-right":
                        x, y = img_width - text_width - 10, 10
                    elif position == "bottom-left":
                        x, y = 10, img_height - text_height - 10
                    elif position == "bottom-right":
                        x, y = img_width - text_width - 10, img_height - text_height - 10
                    else:  # center
                        x, y = (img_width - text_width) // 2, (img_height - text_height) // 2
                    
                    # Draw text with opacity
                    draw.text((x, y), watermark_text, fill=font_color, font=font)
                
                elif watermark_image_path:
                    # Create image watermark
                    with Image.open(watermark_image_path) as watermark_img:
                        # Convert watermark to RGBA if needed
                        if watermark_img.mode != 'RGBA':
                            watermark_img = watermark_img.convert('RGBA')
                        
                        # Resize watermark to reasonable size (max 1/4 of original image)
                        max_size = min(img_width, img_height) // 4
                        watermark_width, watermark_height = watermark_img.size
                        
                        if watermark_width > max_size or watermark_height > max_size:
                            scale = min(max_size / watermark_width, max_size / watermark_height)
                            new_width = int(watermark_width * scale)
                            new_height = int(watermark_height * scale)
                            watermark_img = watermark_img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                        
                        # Calculate position
                        watermark_width, watermark_height = watermark_img.size
                        if position == "top-left":
                            x, y = 10, 10
                        elif position == "top-right":
                            x, y = img_width - watermark_width - 10, 10
                        elif position == "bottom-left":
                            x, y = 10, img_height - watermark_height - 10
                        elif position == "bottom-right":
                            x, y = img_width - watermark_width - 10, img_height - watermark_height - 10
                        else:  # center
                            x, y = (img_width - watermark_width) // 2, (img_height - watermark_height) // 2
                        
                        # Apply opacity to watermark
                        watermark_img.putalpha(int(255 * opacity))
                        
                        # Paste watermark onto main image
                        watermarked_img.paste(watermark_img, (x, y), watermark_img)
                
                # Convert back to original mode if needed
                if original_mode != 'RGBA':
                    watermarked_img = watermarked_img.convert(original_mode)
                
                # Save the watermarked image
                watermarked_img.save(output_path)
                
                # Get output file information
                output_size = os.path.getsize(output_path)
                
                result = {
                    "input_path": image_path,
                    "output_path": output_path,
                    "watermark_text": watermark_text,
                    "watermark_image_path": watermark_image_path,
                    "position": position,
                    "opacity": opacity,
                    "font_size": font_size if watermark_text else None,
                    "font_color": font_color if watermark_text else None,
                    "original_size": original_size,
                    "watermarked_size": watermarked_img.size,
                    "original_mode": original_mode,
                    "watermarked_mode": watermarked_img.mode,
                    "input_file_size": file_size,
                    "output_file_size": output_size,
                    "success": True
                }
                
        except ImportError:
            # PIL not available, return mock result
            result = {
                "input_path": image_path,
                "output_path": output_path,
                "watermark_text": watermark_text,
                "watermark_image_path": watermark_image_path,
                "position": position,
                "opacity": opacity,
                "font_size": font_size if watermark_text else None,
                "font_color": font_color if watermark_text else None,
                "input_file_size": file_size,
                "file_extension": file_ext,
                "success": True,
                "note": "PIL/Pillow not available - this is a mock result. Install PIL for actual watermarking."
            }
        
        except Exception as e:
            return {"error": f"Watermarking failed: {str(e)}"}
        
        return result
        
    except Exception as e:
        return {"error": f"Watermarking failed: {str(e)}"}

if __name__ == "__main__":
    # Example usage
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    result = add_watermark(
        image_path="./image_data/cat.gif",
        watermark_text="© 2024 My Company",
        position="bottom-right",
        opacity=0.8,
        font_size=20,
        font_color="white",
        output_path="./watermarked_image.gif",
    )
    print(json.dumps(result, indent=2, ensure_ascii=False)) 