import os
import json
from PIL import Image

def create_thumbnail_from_image(image_path, size=(150, 150), output_path=None, maintain_aspect_ratio=True, 
                     quality=85, format="JPEG"):
    """
    Create a thumbnail from an image.
    
    Args:
        image_path (str): Path to the input image file
        size (tuple): Thumbnail size (width, height) in pixels
        output_path (str): Path for the output thumbnail
        maintain_aspect_ratio (bool): Whether to maintain aspect ratio
        quality (int): JPEG quality (1-100)
        format (str): Output format - "JPEG", "PNG", "WEBP"
    
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
        
        # Validate size
        if len(size) != 2 or size[0] <= 0 or size[1] <= 0:
            return {
                "success": False,
                "error": "Invalid size. Must be a tuple of two positive integers."
            }
        
        # Open image
        with Image.open(image_path) as img:
            # Convert to RGB if necessary
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            original_size = img.size
            
            # Create thumbnail
            if maintain_aspect_ratio:
                # Use thumbnail method which maintains aspect ratio
                img.thumbnail(size, Image.Resampling.LANCZOS)
                thumbnail_size = img.size
            else:
                # Resize to exact size
                img = img.resize(size, Image.Resampling.LANCZOS)
                thumbnail_size = size
            
            # Determine output path
            if output_path is None:
                base_name = os.path.splitext(image_path)[0]
                if format.upper() == "JPEG":
                    ext = ".jpg"
                elif format.upper() == "PNG":
                    ext = ".png"
                elif format.upper() == "WEBP":
                    ext = ".webp"
                else:
                    ext = ".jpg"
                output_path = f"{base_name}_thumb{ext}"
            
            # Save thumbnail
            if format.upper() == "JPEG":
                img.save(output_path, "JPEG", quality=quality)
            elif format.upper() == "PNG":
                img.save(output_path, "PNG")
            elif format.upper() == "WEBP":
                img.save(output_path, "WEBP", quality=quality)
            else:
                img.save(output_path, "JPEG", quality=quality)
            
            return {
                "success": True,
                "output_path": output_path,
                "original_size": f"{original_size[0]}x{original_size[1]}",
                "thumbnail_size": f"{thumbnail_size[0]}x{thumbnail_size[1]}",
                "target_size": f"{size[0]}x{size[1]}",
                "maintain_aspect_ratio": maintain_aspect_ratio,
                "quality": quality,
                "format": format.upper()
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": f"Error creating thumbnail: {str(e)}"
        }

if __name__ == "__main__":
    # Test the function
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    result = create_thumbnail_from_image(
        image_path="./image_data/dog.jpg",
        size=(150, 150),
        output_path="test_thumbnail.jpg"
    )
    print(json.dumps(result, indent=2)) 