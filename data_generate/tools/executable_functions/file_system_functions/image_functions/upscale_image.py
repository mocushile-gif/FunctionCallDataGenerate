import os
import json
from PIL import Image, ImageEnhance
import cv2
import numpy as np
from typing import Dict, Any, Optional
from dotenv import load_dotenv
load_dotenv()

def upscale_image(input_path: str, output_path: str = None,
                  scale_factor: float = 2.0, method: str = "lanczos",
                  preserve_quality: bool = True, output_format: str = "png"):
    """
    Upscale an image to higher resolution.
    
    Parameters:
    - input_path (str): Path to input image file
    - output_path (str): Path for output file (optional, auto-generated if not provided)
    - scale_factor (float): Scale factor for upscaling (1.0-4.0)
    - method (str): Upscaling method ("lanczos", "bicubic", "bilinear", "nearest")
    - preserve_quality (bool): Whether to preserve image quality during upscaling
    - output_format (str): Output image format ("png", "jpg", "tiff")
    
    Returns:
    - dict: Upscaling result information
    """
    
    try:
        # Validate parameters
        if not input_path or not os.path.exists(input_path):
            return {"error": "Input image file not found"}
        
        if scale_factor < 1.0 or scale_factor > 4.0:
            return {"error": "Scale factor must be between 1.0 and 4.0"}
        
        if method not in ["lanczos", "bicubic", "bilinear", "nearest"]:
            return {"error": "Method must be 'lanczos', 'bicubic', 'bilinear', or 'nearest'"}
        
        if output_format not in ["png", "jpg", "tiff"]:
            return {"error": "Output format must be 'png', 'jpg', or 'tiff'"}
        
        # Set output path if not provided
        if not output_path:
            base_name = os.path.splitext(os.path.basename(input_path))[0]
            output_path = f"{base_name}_upscaled.{output_format}"
        
        # Load image
        image = Image.open(input_path)
        original_size = image.size
        
        # Calculate new size
        new_width = int(original_size[0] * scale_factor)
        new_height = int(original_size[1] * scale_factor)
        new_size = (new_width, new_height)
        
        # Apply upscaling based on method
        if method == "lanczos":
            result_image = upscale_lanczos(image, new_size, preserve_quality)
        elif method == "bicubic":
            result_image = upscale_bicubic(image, new_size, preserve_quality)
        elif method == "bilinear":
            result_image = upscale_bilinear(image, new_size, preserve_quality)
        elif method == "nearest":
            result_image = upscale_nearest(image, new_size, preserve_quality)
        
        # Save result
        save_options = {}
        if output_format == "jpg":
            save_options["quality"] = 95 if preserve_quality else 85
        elif output_format == "png":
            save_options["optimize"] = True
        
        result_image.save(output_path, **save_options)
        
        # Calculate quality metrics
        quality_metrics = calculate_quality_metrics(image, result_image)
        
        result = {
            "input_file": input_path,
            "output_path": output_path,
            "scale_factor": scale_factor,
            "method": method,
            "preserve_quality": preserve_quality,
            "output_format": output_format,
            "original_size": original_size,
            "new_size": new_size,
            "pixel_increase": new_width * new_height - original_size[0] * original_size[1],
            "quality_metrics": quality_metrics,
            "success": True
        }
        
        # Add file information
        if os.path.exists(output_path):
            result["input_size"] = os.path.getsize(input_path)
            result["output_size"] = os.path.getsize(output_path)
            result["size_ratio"] = round(result["output_size"] / result["input_size"], 3)
        
        return result
        
    except Exception as e:
        return {"error": f"Error upscaling image: {str(e)}"}

def upscale_lanczos(image: Image.Image, new_size: tuple, preserve_quality: bool) -> Image.Image:
    """Upscale using Lanczos resampling."""
    # Lanczos is generally the best for upscaling
    resampling = Image.Resampling.LANCZOS
    
    # Upscale
    upscaled = image.resize(new_size, resampling)
    
    # Apply quality enhancements if requested
    if preserve_quality:
        upscaled = enhance_quality(upscaled)
    
    return upscaled

def upscale_bicubic(image: Image.Image, new_size: tuple, preserve_quality: bool) -> Image.Image:
    """Upscale using bicubic interpolation."""
    resampling = Image.Resampling.BICUBIC
    
    # Upscale
    upscaled = image.resize(new_size, resampling)
    
    # Apply quality enhancements if requested
    if preserve_quality:
        upscaled = enhance_quality(upscaled)
    
    return upscaled

def upscale_bilinear(image: Image.Image, new_size: tuple, preserve_quality: bool) -> Image.Image:
    """Upscale using bilinear interpolation."""
    resampling = Image.Resampling.BILINEAR
    
    # Upscale
    upscaled = image.resize(new_size, resampling)
    
    # Apply quality enhancements if requested
    if preserve_quality:
        upscaled = enhance_quality(upscaled)
    
    return upscaled

def upscale_nearest(image: Image.Image, new_size: tuple, preserve_quality: bool) -> Image.Image:
    """Upscale using nearest neighbor interpolation."""
    resampling = Image.Resampling.NEAREST
    
    # Upscale
    upscaled = image.resize(new_size, resampling)
    
    # Apply quality enhancements if requested
    if preserve_quality:
        upscaled = enhance_quality(upscaled)
    
    return upscaled

def enhance_quality(image: Image.Image) -> Image.Image:
    """Apply quality enhancement techniques."""
    # Slight sharpening
    enhancer = ImageEnhance.Sharpness(image)
    image = enhancer.enhance(1.1)
    
    # Slight contrast enhancement
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(1.05)
    
    return image

def calculate_quality_metrics(original: Image.Image, upscaled: Image.Image) -> Dict[str, float]:
    """Calculate quality metrics for upscaled image."""
    try:
        # Resize upscaled image back to original size for comparison
        temp_upscaled = upscaled.resize(original.size, Image.Resampling.LANCZOS)
        
        # Convert to numpy arrays
        original_array = np.array(original.convert('L'))  # Convert to grayscale
        upscaled_array = np.array(temp_upscaled.convert('L'))
        
        # Calculate MSE (Mean Squared Error)
        mse = np.mean((original_array.astype(float) - upscaled_array.astype(float)) ** 2)
        
        # Calculate PSNR (Peak Signal-to-Noise Ratio)
        psnr = 20 * np.log10(255.0 / np.sqrt(mse)) if mse > 0 else float('inf')
        
        # Calculate SSIM-like metric (simplified)
        original_mean = np.mean(original_array)
        upscaled_mean = np.mean(upscaled_array)
        original_var = np.var(original_array)
        upscaled_var = np.var(upscaled_array)
        
        # Simplified SSIM calculation
        c1 = (0.01 * 255) ** 2
        c2 = (0.03 * 255) ** 2
        
        numerator = (2 * original_mean * upscaled_mean + c1) * (2 * np.cov(original_array.flatten(), upscaled_array.flatten())[0, 1] + c2)
        denominator = (original_mean ** 2 + upscaled_mean ** 2 + c1) * (original_var + upscaled_var + c2)
        
        ssim = numerator / denominator if denominator > 0 else 0
        
        return {
            "mse": round(mse, 2),
            "psnr": round(psnr, 2) if psnr != float('inf') else 0,
            "ssim": round(ssim, 3)
        }
        
    except Exception as e:
        return {
            "mse": 0,
            "psnr": 0,
            "ssim": 0
        }


if __name__ == "__main__":
    # Example usage
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    result = upscale_image("./image_data/dog.jpg", scale_factor=2.0, method="lanczos")
    print(json.dumps(result, indent=2)) 
