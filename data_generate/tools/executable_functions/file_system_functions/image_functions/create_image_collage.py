import os
import json
from PIL import Image
import math
from dotenv import load_dotenv
load_dotenv()

def create_image_collage(image_paths, layout="grid", output_path=None, background_color=(255, 255, 255), 
                   spacing=10, max_width=1200, max_height=800):
    """
    Create a collage from multiple images.
    
    Args:
        image_paths (list): List of paths to input images
        layout (str): Layout type - "grid", "horizontal", "vertical", "mosaic"
        output_path (str): Path for the output collage image
        background_color (tuple): Background color (R, G, B)
        spacing (int): Spacing between images in pixels
        max_width (int): Maximum width of the collage
        max_height (int): Maximum height of the collage
    
    Returns:
        dict: Result information including success status and output path
    """
    
    try:
        # Validate input files
        valid_images = []
        for img_path in image_paths:
            if os.path.exists(img_path):
                valid_images.append(img_path)
            else:
                print(f"Warning: Image file not found: {img_path}")
        
        if not valid_images:
            return {
                "success": False,
                "error": "No valid image files found"
            }
        
        # Load and resize images
        images = []
        for img_path in valid_images:
            with Image.open(img_path) as img:
                # Convert to RGB if necessary
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                images.append(img.copy())
        
        # Calculate layout
        num_images = len(images)
        
        if layout == "grid":
            # Calculate grid dimensions
            cols = math.ceil(math.sqrt(num_images))
            rows = math.ceil(num_images / cols)
            
            # Calculate individual image size
            max_img_width = (max_width - (cols - 1) * spacing) // cols
            max_img_height = (max_height - (rows - 1) * spacing) // rows
            
            # Resize images to fit
            resized_images = []
            for img in images:
                img.thumbnail((max_img_width, max_img_height), Image.Resampling.LANCZOS)
                resized_images.append(img)
            
            # Create collage
            collage_width = cols * max_img_width + (cols - 1) * spacing
            collage_height = rows * max_img_height + (rows - 1) * spacing
            
            collage = Image.new('RGB', (collage_width, collage_height), background_color)
            
            for i, img in enumerate(resized_images):
                row = i // cols
                col = i % cols
                x = col * (max_img_width + spacing)
                y = row * (max_img_height + spacing)
                collage.paste(img, (x, y))
                
        elif layout == "horizontal":
            # Calculate total width and max height
            total_width = sum(img.width for img in images) + (len(images) - 1) * spacing
            max_img_height = max(img.height for img in images)
            
            # Scale if too wide
            if total_width > max_width:
                scale_factor = max_width / total_width
                total_width = max_width
                max_img_height = int(max_img_height * scale_factor)
                
                # Resize images
                resized_images = []
                for img in images:
                    new_width = int(img.width * scale_factor)
                    new_height = int(img.height * scale_factor)
                    img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                    resized_images.append(img)
            else:
                resized_images = images
            
            # Create collage
            collage = Image.new('RGB', (total_width, max_img_height), background_color)
            x_offset = 0
            for img in resized_images:
                y_offset = (max_img_height - img.height) // 2
                collage.paste(img, (x_offset, y_offset))
                x_offset += img.width + spacing
                
        elif layout == "vertical":
            # Calculate max width and total height
            max_img_width = max(img.width for img in images)
            total_height = sum(img.height for img in images) + (len(images) - 1) * spacing
            
            # Scale if too tall
            if total_height > max_height:
                scale_factor = max_height / total_height
                max_img_width = int(max_img_width * scale_factor)
                total_height = max_height
                
                # Resize images
                resized_images = []
                for img in images:
                    new_width = int(img.width * scale_factor)
                    new_height = int(img.height * scale_factor)
                    img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                    resized_images.append(img)
            else:
                resized_images = images
            
            # Create collage
            collage = Image.new('RGB', (max_img_width, total_height), background_color)
            y_offset = 0
            for img in resized_images:
                x_offset = (max_img_width - img.width) // 2
                collage.paste(img, (x_offset, y_offset))
                y_offset += img.height + spacing
                
        elif layout == "mosaic":
            # Create a more artistic mosaic layout
            # This is a simplified version - could be enhanced with more complex algorithms
            if num_images < 4:
                return create_image_collage(image_paths, "grid", output_path, background_color, spacing, max_width, max_height)
            
            # Use golden ratio for more pleasing layout
            cols = math.ceil(math.sqrt(num_images * 1.618))
            rows = math.ceil(num_images / cols)
            
            # Calculate individual image size
            max_img_width = (max_width - (cols - 1) * spacing) // cols
            max_img_height = (max_height - (rows - 1) * spacing) // rows
            
            # Resize images to fit
            resized_images = []
            for img in images:
                img.thumbnail((max_img_width, max_img_height), Image.Resampling.LANCZOS)
                resized_images.append(img)
            
            # Create collage with some images larger
            collage_width = cols * max_img_width + (cols - 1) * spacing
            collage_height = rows * max_img_height + (rows - 1) * spacing
            
            collage = Image.new('RGB', (collage_width, collage_height), background_color)
            
            for i, img in enumerate(resized_images):
                row = i // cols
                col = i % cols
                x = col * (max_img_width + spacing)
                y = row * (max_img_height + spacing)
                
                # Make some images larger for mosaic effect
                if i % 3 == 0 and i + 1 < len(resized_images):
                    # Double size for some images
                    img = img.resize((max_img_width * 2, max_img_height * 2), Image.Resampling.LANCZOS)
                    collage.paste(img, (x, y))
                else:
                    collage.paste(img, (x, y))
        
        else:
            return {
                "success": False,
                "error": f"Unsupported layout: {layout}"
            }
        
        # Determine output path
        if output_path is None:
            output_path = f"collage_{layout}_{len(valid_images)}_images.jpg"
        
        # Save collage
        collage.save(output_path, quality=95)
        
        return {
            "success": True,
            "output_path": output_path,
            "layout": layout,
            "num_images": len(valid_images),
            "collage_size": f"{collage.width}x{collage.height}",
            "valid_images": valid_images
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Error creating collage: {str(e)}"
        }

if __name__ == "__main__":
    # Test the function
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    result = create_image_collage(
        image_paths=["./image_data/dog.jpg", "./image_data/cat.gif"],
        layout="grid",
        output_path="test_collage.jpg"
    )
    print(json.dumps(result, indent=2)) 