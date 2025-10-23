import os
import json
from PIL import Image, ImageFilter, ImageEnhance
import numpy as np
import cv2
from typing import Dict, Any, Optional
from dotenv import load_dotenv
load_dotenv()

def remove_image_background(input_path: str, output_path: str = None,
                     method: str = "auto", threshold: float = 0.5,
                     output_format: str = "png"):
    """
    Remove background from an image.
    
    Parameters:
    - input_path (str): Path to input image file
    - output_path (str): Path for output file (optional, auto-generated if not provided)
    - method (str): Background removal method ("auto", "color", "edge", "ai")
    - threshold (float): Threshold for background detection (0.0-1.0)
    - output_format (str): Output image format ("png", "jpg", "webp")
    
    Returns:
    - dict: Background removal result information
    """
    
    try:
        # Validate parameters
        if not input_path or not os.path.exists(input_path):
            return {"error": "Input image file not found"}
        
        if method not in ["auto", "color", "edge", "ai"]:
            return {"error": "Method must be 'auto', 'color', 'edge', or 'ai'"}
        
        if threshold < 0.0 or threshold > 1.0:
            return {"error": "Threshold must be between 0.0 and 1.0"}
        
        if output_format not in ["png", "jpg", "webp"]:
            return {"error": "Output format must be 'png', 'jpg', or 'webp'"}
        
        # Set output path if not provided
        if not output_path:
            base_name = os.path.splitext(os.path.basename(input_path))[0]
            output_path = f"{base_name}_no_bg.{output_format}"
        
        # Load image
        image = Image.open(input_path)
        original_size = image.size
        
        # Convert to RGBA if not already
        if image.mode != 'RGBA':
            image = image.convert('RGBA')
        
        # Apply background removal based on method
        if method == "auto":
            # Try AI method first, fallback to color-based
            try:
                result_image = remove_background_ai(image)
                if result_image is None:
                    result_image = remove_background_color(image, threshold)
            except:
                result_image = remove_background_color(image, threshold)
        
        elif method == "color":
            result_image = remove_background_color(image, threshold)
        
        elif method == "edge":
            result_image = remove_background_edge(image, threshold)
        
        elif method == "ai":
            result_image = remove_background_ai(image)
            if result_image is None:
                return {"error": "AI background removal failed, try another method"}
        
        # Save result
        result_image.save(output_path, format=output_format.upper())
        
        # Calculate statistics
        original_pixels = original_size[0] * original_size[1]
        result_pixels = result_image.size[0] * result_image.size[1]
        
        # Count transparent pixels
        transparent_pixels = 0
        if result_image.mode == 'RGBA':
            data = np.array(result_image)
            transparent_pixels = np.sum(data[:, :, 3] == 0)
        
        transparency_ratio = transparent_pixels / result_pixels if result_pixels > 0 else 0
        
        result = {
            "input_file": input_path,
            "output_path": output_path,
            "method": method,
            "threshold": threshold,
            "output_format": output_format,
            "original_size": original_size,
            "result_size": result_image.size,
            "transparency_ratio": round(transparency_ratio, 3),
            "transparent_pixels": int(transparent_pixels),
            "total_pixels": result_pixels,
            "operation": "remove_background",
            "parameters": {
                "method": method,
                "threshold": threshold,
                "output_format": output_format
            },
            "success": True
        }
        
        # Add file information
        if os.path.exists(output_path):
            result["input_size"] = os.path.getsize(input_path)
            result["output_size"] = os.path.getsize(output_path)
            result["compression_ratio"] = round(result["output_size"] / result["input_size"], 3)
        
        return result
        
    except Exception as e:
        return {"error": f"Error removing background: {str(e)}"}

def remove_background_color(image: Image.Image, threshold: float) -> Image.Image:
    """Remove background based on color similarity."""
    try:
        # Convert to numpy array
        data = np.array(image)
        
        # Get the most common color (assumed to be background)
        pixels = data.reshape(-1, 4)
        unique_colors, counts = np.unique(pixels, axis=0, return_counts=True)
        background_color = unique_colors[np.argmax(counts)]
        
        # Create mask for similar colors
        color_diff = np.sqrt(np.sum((pixels - background_color) ** 2, axis=1))
        mask = color_diff > (threshold * 255)
        
        # Apply mask
        pixels[mask == False, 3] = 0  # Set alpha to 0 for background
        
        # Reshape back to image
        result_data = pixels.reshape(data.shape)
        return Image.fromarray(result_data)
        
    except Exception as e:
        raise Exception(f"Color-based background removal failed: {str(e)}")

def remove_background_edge(image: Image.Image, threshold: float) -> Image.Image:
    """Remove background based on edge detection."""
    try:
        # Convert to numpy array
        data = np.array(image)
        
        # Convert to grayscale for edge detection
        gray = cv2.cvtColor(data, cv2.COLOR_RGBA2GRAY)
        
        # Apply edge detection
        edges = cv2.Canny(gray, 50, 150)
        
        # Dilate edges to create mask
        kernel = np.ones((3, 3), np.uint8)
        dilated = cv2.dilate(edges, kernel, iterations=2)
        
        # Create mask from edges
        mask = dilated > 0
        
        # Apply mask to alpha channel
        data[:, :, 3] = data[:, :, 3] * mask
        
        return Image.fromarray(data)
        
    except Exception as e:
        raise Exception(f"Edge-based background removal failed: {str(e)}")

def remove_background_ai(image: Image.Image) -> Optional[Image.Image]:
    """Remove background using AI-based approach (placeholder)."""
    try:
        # This is a placeholder for AI-based background removal
        # In a real implementation, you would use a pre-trained model
        # like rembg, backgroundremover, or similar libraries
        
        # For now, return None to indicate AI method is not available
        return None
        
    except Exception as e:
        raise Exception(f"AI-based background removal failed: {str(e)}")

if __name__ == "__main__":
    # Example usage
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    result = remove_image_background("./image_data/dog.jpg", method="color", threshold=0.3)
    print(json.dumps(result, indent=2)) 