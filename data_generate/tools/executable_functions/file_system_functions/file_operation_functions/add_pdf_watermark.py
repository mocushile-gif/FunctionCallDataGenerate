import os
import json
from typing import Dict, Any, Optional
from PIL import Image, ImageDraw, ImageFont
import fitz  # PyMuPDF
import io
from dotenv import load_dotenv
load_dotenv()

def add_pdf_watermark(input_path: str, watermark_text: str = "", 
                     watermark_image: str = None, output_path: str = None,
                     position: str = "center", opacity: float = 0.5,
                     font_size: int = 24, font_color: str = "#FF0000",
                     rotation: int = 0):
    """
    Add watermark to a PDF file.
    
    Parameters:
    - input_path (str): Path to input PDF file
    - watermark_text (str): Text watermark
    - watermark_image (str): Path to image watermark (optional)
    - output_path (str): Path for output file (optional, auto-generated if not provided)
    - position (str): Watermark position ("top-left", "top-right", "center", "bottom-left", "bottom-right")
    - opacity (float): Watermark opacity (0.0-1.0)
    - font_size (int): Font size for text watermark
    - font_color (str): Font color (hex code)
    - rotation (int): Rotation angle in degrees
    
    Returns:
    - dict: Watermark result information
    """

    # Validate parameters
    if not input_path or not os.path.exists(input_path):
        return {"error": "Input PDF file not found"}
    
    if not input_path.lower().endswith('.pdf'):
        return {"error": "Input file must be a PDF"}
    
    if not watermark_text and not watermark_image:
        return {"error": "Either watermark_text or watermark_image must be provided"}
    
    if watermark_image and not os.path.exists(watermark_image):
        return {"error": "Watermark image file not found"}
    
    if position not in ["top-left", "top-right", "center", "bottom-left", "bottom-right"]:
        return {"error": "Position must be one of: top-left, top-right, center, bottom-left, bottom-right"}
    
    if opacity < 0.0 or opacity > 1.0:
        return {"error": "Opacity must be between 0.0 and 1.0"}
    
    if font_size < 1 or font_size > 200:
        return {"error": "Font size must be between 1 and 200"}
    
    if rotation not in [0, 90, 180, 270]:
        return {"error": "Rotation must be one of: 0, 90, 180, 270"}


    # Set output path if not provided
    if not output_path:
        base_name = os.path.splitext(os.path.basename(input_path))[0]
        output_path = f"{base_name}_watermarked.pdf"
    
    # Open PDF
    doc = fitz.open(input_path)
    
    # Create watermark
    watermark_type = "text" if watermark_text else "image"
    
    if watermark_type == "text":
        # Create text watermark
        watermark = create_text_watermark(watermark_text, font_size, font_color, opacity)
    else:
        # Load image watermark
        watermark = load_image_watermark(watermark_image, opacity)
    
    # Calculate position coordinates
    position_coords = calculate_position(position, doc[0].rect, watermark.size)
    
    # Add watermark to each page
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
    
        # 将 Pillow Image 转为 PNG 字节流
        img_bytes = io.BytesIO()
        watermark.save(img_bytes, format='PNG')
        img_bytes.seek(0)

        # 在页面上插入图像（从字节流创建 Pixmap）
        page.insert_image(
            fitz.Rect(position_coords[0], position_coords[1],
                    position_coords[0] + watermark.size[0],
                    position_coords[1] + watermark.size[1]),
            stream=img_bytes.read(),
            rotate=rotation,
            overlay=True
        )
    
    result = {
        "input_file": input_path,
        "output_path": output_path,
        "watermark_type": watermark_type,
        "watermark_content": watermark_text if watermark_type == "text" else watermark_image,
        "position": position,
        "opacity": opacity,
        "font_size": font_size if watermark_type == "text" else None,
        "font_color": font_color if watermark_type == "text" else None,
        "rotation": rotation,
        "total_pages": len(doc),
        "success": True
    }
    
    # Save watermarked PDF
    doc.save(output_path)
    doc.close()
    
    # Add file information
    if os.path.exists(output_path):
        result["input_size"] = os.path.getsize(input_path)
        result["output_size"] = os.path.getsize(output_path)
        result["size_difference"] = result["output_size"] - result["input_size"]
    
    return result


def create_text_watermark(text: str, font_size: int, color: str, opacity: float):
    """Create a text watermark image."""
    try:
        
        # Create a transparent image
        img = Image.new('RGBA', (400, 100), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Try to use a default font
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            font = ImageFont.load_default()
        
        # Get text size
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # Create new image with proper size
        img = Image.new('RGBA', (text_width + 20, text_height + 20), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Convert hex color to RGB
        color_rgb = tuple(int(color[i:i+2], 16) for i in (1, 3, 5))  # Remove # and convert
        
        # Draw text
        draw.text((10, 10), text, font=font, fill=color_rgb + (int(255 * opacity),))
        
        return img
        
    except Exception as e:
        raise Exception(f"Error creating text watermark: {str(e)}")

def load_image_watermark(image_path: str, opacity: float):
    """Load and process image watermark."""
    # Load image
    img = Image.open(image_path)
    
    # Convert to RGBA if needed
    if img.mode != 'RGBA':
        img = img.convert('RGBA')
    
    # Apply opacity
    if opacity < 1.0:
        data = img.getdata()
        new_data = []
        for item in data:
            new_data.append((item[0], item[1], item[2], int(item[3] * opacity)))
        img.putdata(new_data)
    
    return img

def calculate_position(position: str, page_rect, watermark_size):
    """Calculate watermark position coordinates."""
    page_width = page_rect.width
    page_height = page_rect.height
    watermark_width = watermark_size[0]
    watermark_height = watermark_size[1]
    
    if position == "top-left":
        return (10, 10)
    elif position == "top-right":
        return (page_width - watermark_width - 10, 10)
    elif position == "center":
        return ((page_width - watermark_width) / 2, (page_height - watermark_height) / 2)
    elif position == "bottom-left":
        return (10, page_height - watermark_height - 10)
    elif position == "bottom-right":
        return (page_width - watermark_width - 10, page_height - watermark_height - 10)
    else:
        return (10, 10)  # Default to top-left


if __name__ == "__main__":
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    result = add_pdf_watermark("./pdf_data/order.pdf", "CONFIDENTIAL", position="center", opacity=0.3)
    print(json.dumps(result, indent=2)) 