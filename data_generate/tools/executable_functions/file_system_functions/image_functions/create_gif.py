import os
import json
from PIL import Image
import math
from dotenv import load_dotenv
load_dotenv()

def create_gif(image_paths, output_path=None, duration=500, loop=0, optimize=True, 
               resize_to=None, quality=85):
    """
    Create a GIF animation from multiple images.
    
    Args:
        image_paths (list): List of paths to input images
        output_path (str): Path for the output GIF file
        duration (int): Duration for each frame in milliseconds
        loop (int): Number of loops (0 for infinite)
        optimize (bool): Whether to optimize the GIF
        resize_to (tuple): Resize all images to this size (width, height)
        quality (int): GIF quality (1-100)
    
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
        
        # Load and process images
        images = []
        for img_path in valid_images:
            with Image.open(img_path) as img:
                # Convert to RGB if necessary
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Resize if requested
                if resize_to:
                    img = img.resize(resize_to, Image.Resampling.LANCZOS)
                
                images.append(img.copy())
        
        # Determine output path
        if output_path is None:
            output_path = f"animation_{len(valid_images)}_frames.gif"
        
        # Save as GIF
        if len(images) == 1:
            # Single image - save as static GIF
            images[0].save(
                output_path,
                format='GIF',
                duration=duration,
                loop=loop,
                optimize=optimize
            )
        else:
            # Multiple images - save as animated GIF
            images[0].save(
                output_path,
                format='GIF',
                save_all=True,
                append_images=images[1:],
                duration=duration,
                loop=loop,
                optimize=optimize
            )
        
        return {
            "success": True,
            "output_path": output_path,
            "num_frames": len(images),
            "duration_per_frame": duration,
            "total_duration": duration * len(images),
            "loop": loop,
            "optimize": optimize,
            "valid_images": valid_images
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Error creating GIF: {str(e)}"
        }

def create_gif_from_video_frames(frame_paths, output_path=None, fps=10, loop=0, 
                                optimize=True, resize_to=None):
    """
    Create a GIF from video frames with specified FPS.
    
    Args:
        frame_paths (list): List of paths to frame images
        output_path (str): Path for the output GIF file
        fps (int): Frames per second
        loop (int): Number of loops (0 for infinite)
        optimize (bool): Whether to optimize the GIF
        resize_to (tuple): Resize all frames to this size (width, height)
    
    Returns:
        dict: Result information including success status and output path
    """
    try:
        # Calculate duration from FPS
        duration = int(1000 / fps)  # Convert to milliseconds
        
        return create_gif(
            image_paths=frame_paths,
            output_path=output_path,
            duration=duration,
            loop=loop,
            optimize=optimize,
            resize_to=resize_to
        )
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Error creating GIF from frames: {str(e)}"
        }

def create_zoom_gif(image_path, output_path=None, zoom_factor=2.0, num_frames=10, 
                   duration=100, loop=0, center=None):
    """
    Create a zoom effect GIF from a single image.
    
    Args:
        image_path (str): Path to the input image
        output_path (str): Path for the output GIF file
        zoom_factor (float): Maximum zoom factor
        num_frames (int): Number of frames in the animation
        duration (int): Duration for each frame in milliseconds
        loop (int): Number of loops (0 for infinite)
        center (tuple): Zoom center point (x, y), None for image center
    
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
        
        # Load image
        with Image.open(image_path) as img:
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            original_width, original_height = img.size
            
            # Determine zoom center
            if center is None:
                center_x, center_y = original_width // 2, original_height // 2
            else:
                center_x, center_y = center
            
            # Create frames
            frames = []
            for i in range(num_frames):
                # Calculate zoom factor for this frame
                current_zoom = 1.0 + (zoom_factor - 1.0) * (i / (num_frames - 1))
                
                # Calculate new size
                new_width = int(original_width * current_zoom)
                new_height = int(original_height * current_zoom)
                
                # Resize image
                resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                # Calculate crop area to maintain original size
                crop_left = max(0, (new_width - original_width) // 2)
                crop_top = max(0, (new_height - original_height) // 2)
                crop_right = crop_left + original_width
                crop_bottom = crop_top + original_height
                
                # Crop to original size
                frame = resized.crop((crop_left, crop_top, crop_right, crop_bottom))
                frames.append(frame)
            
            # Determine output path
            if output_path is None:
                base_name = os.path.splitext(image_path)[0]
                output_path = f"{base_name}_zoom.gif"
            
            # Save as GIF
            frames[0].save(
                output_path,
                format='GIF',
                save_all=True,
                append_images=frames[1:],
                duration=duration,
                loop=loop,
                optimize=True
            )
            
            return {
                "success": True,
                "output_path": output_path,
                "num_frames": num_frames,
                "zoom_factor": zoom_factor,
                "duration_per_frame": duration,
                "total_duration": duration * num_frames,
                "loop": loop
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": f"Error creating zoom GIF: {str(e)}"
        }

if __name__ == "__main__":
    # Test the function
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    result = create_gif(
        image_paths=["./image_data/dog.jpg", "./image_data/chat.png"],
        output_path="test_animation.gif",
        duration=500
    )
    print(json.dumps(result, indent=2)) 