import os
import json
from typing import Dict, Any, Optional
from PIL import Image, ImageFilter, ImageEnhance, ImageOps
import numpy as np
import cv2
from dotenv import load_dotenv
load_dotenv()

def apply_style_transfer(input_path: str, style_path: str = None, 
                        style_type: str = "artistic", output_path: str = None,
                        intensity: float = 0.5, preserve_colors: bool = True,):
    """
    Apply style transfer to an image.
    
    Parameters:
    - input_path (str): Path to input image file
    - style_path (str): Path to style image file (optional for preset styles)
    - style_type (str): Style type ("artistic", "vintage", "sketch", "cartoon", "watercolor")
    - output_path (str): Path for output file (optional, auto-generated if not provided)
    - intensity (float): Style transfer intensity (0.0-1.0)
    - preserve_colors: Whether to preserve original colors
    
    Returns:
    - dict: Style transfer result information
    """
    
    
    # Validate parameters
    if not input_path or not os.path.exists(input_path):
        return {"error": "Input image file not found"}
    
    if style_path and not os.path.exists(style_path):
        return {"error": "Style image file not found"}
    
    if style_type not in ["artistic", "vintage", "sketch", "cartoon", "watercolor"]:
        return {"error": "Style type must be one of: artistic, vintage, sketch, cartoon, watercolor"}
    
    if intensity < 0.0 or intensity > 1.0:
        return {"error": "Intensity must be between 0.0 and 1.0"}
    
    # Set output path if not provided
    if not output_path:
        base_name = os.path.splitext(os.path.basename(input_path))[0]
        output_path = f"{base_name}_{style_type}.jpg"
    
    # Load input image
    image = Image.open(input_path)
    original_size = image.size
    
    # Apply style transfer based on type
    if style_type == "artistic":
        result_image = apply_artistic_style(image, intensity, preserve_colors)
    elif style_type == "vintage":
        result_image = apply_vintage_style(image, intensity, preserve_colors)
    elif style_type == "sketch":
        result_image = apply_sketch_style(image, intensity)
    elif style_type == "cartoon":
        result_image = apply_cartoon_style(image, intensity)
    elif style_type == "watercolor":
        result_image = apply_watercolor_style(image, intensity)
    
    # Save result
    result_image.save(output_path, quality=95)
    
    result = {
        "input_file": input_path,
        "style_file": style_path,
        "style_type": style_type,
        "output_path": output_path,
        "intensity": intensity,
        "preserve_colors": preserve_colors,
        "original_size": original_size,
        "result_size": result_image.size,
        "success": True
    }
    
    # Add file information
    if os.path.exists(output_path):
        result["input_size"] = os.path.getsize(input_path)
        result["output_size"] = os.path.getsize(output_path)
        result["compression_ratio"] = round(result["output_size"] / result["input_size"], 3)
    
    return result

def apply_artistic_style(image: Image.Image, intensity: float, preserve_colors: bool) -> Image.Image:
    """Apply artistic style effects."""
    # Enhance contrast and saturation
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(1.0 + intensity * 0.5)
    
    enhancer = ImageEnhance.Color(image)
    image = enhancer.enhance(1.0 + intensity * 0.8)
    
    # Apply slight blur for artistic effect
    if intensity > 0.3:
        image = image.filter(ImageFilter.GaussianBlur(radius=intensity * 2))
    
    return image

def match_size(img: np.ndarray, target: np.ndarray) -> np.ndarray:
    if img.shape[:2] != target.shape[:2]:
        return cv2.resize(img, (target.shape[1], target.shape[0]))
    return img

def apply_vintage_style(image: Image.Image, intensity: float, preserve_colors: bool) -> Image.Image:
    """Apply vintage/retro style effects."""
    # Convert to sepia tone
    data = np.array(image)
    if data.shape[0] < 3 or data.shape[1] < 3:
        raise ValueError("Image too small for filter")

    if not preserve_colors:
        image = image.convert('RGB')
        
        # Sepia transformation
        sepia_matrix = np.array([
            [0.393, 0.769, 0.189],
            [0.349, 0.686, 0.168],
            [0.272, 0.534, 0.131]
        ])
        
        sepia_data = np.dot(data, sepia_matrix.T)
        sepia_data = np.clip(sepia_data, 0, 255).astype(np.uint8)
        image = Image.fromarray(sepia_data)
    
    # Reduce saturation
    enhancer = ImageEnhance.Color(image)
    image = enhancer.enhance(0.7 + intensity * 0.3)
    
    # Add vintage noise
    if intensity > 0.5:
        noise = np.random.normal(0, intensity * 20, image.size + (3,))
        noise = match_size(noise, data)
        data = np.array(image)
        data = np.clip(data + noise, 0, 255).astype(np.uint8)
        image = Image.fromarray(data)
    
    return image

def apply_sketch_style(image: Image.Image, intensity: float) -> Image.Image:
    """Apply sketch/pencil drawing style."""
    # Convert to grayscale
    gray = image.convert('L')
    
    # Invert the image
    inverted = ImageOps.invert(gray)
    
    # Apply Gaussian blur
    blurred = inverted.filter(ImageFilter.GaussianBlur(radius=intensity * 5))

    # Blend with original
    result = Image.blend(gray, blurred, intensity)
    
    return result


def apply_cartoon_style(image: Image.Image, intensity: float) -> Image.Image:
    """Apply cartoon/anime style effects."""
    # Convert to numpy array
    data = np.array(image)
    
    # Edge detection
    gray = cv2.cvtColor(data, cv2.COLOR_RGB2GRAY)
    edges = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, 2)
    
    # Color quantization
    data_float = data.astype(np.float32)
    data_quantized = data_float / 255.0
    data_quantized = np.round(data_quantized * (8 - intensity * 4)) / (8 - intensity * 4)
    data_quantized = (data_quantized * 255).astype(np.uint8)
    
    # Apply bilateral filter for smoothing
    smoothed = cv2.bilateralFilter(data_quantized, 9, 75, 75)
    
    # Combine edges with smoothed image
    edges_rgb = cv2.cvtColor(edges, cv2.COLOR_GRAY2RGB)
    
    # Ensure edges match the shape of smoothed image
    edges_rgb = match_size(edges_rgb, smoothed)
    result = cv2.bitwise_and(smoothed, edges_rgb)

    return Image.fromarray(result)

def apply_watercolor_style(image: Image.Image, intensity: float) -> Image.Image:
    """Apply watercolor painting style."""
    # Apply bilateral filter for edge-preserving smoothing
    data = np.array(image)
    smoothed = cv2.bilateralFilter(data, 15, 80, 80)
    
    # Enhance colors
    enhanced = cv2.convertScaleAbs(smoothed, alpha=1.0 + intensity * 0.3, beta=intensity * 10)
    enhanced = match_size(enhanced, data)
    # Add slight blur for watercolor effect
    if intensity > 0.3:
        enhanced = cv2.GaussianBlur(enhanced, (3, 3), intensity * 2)
    
    return Image.fromarray(enhanced)

if __name__ == "__main__":
    # Example usage
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    result = apply_style_transfer("./image_data/dog.jpg", style_type="watercolor", intensity=0.7)
    print(json.dumps(result, indent=2)) 