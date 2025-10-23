import os
import json
import cv2
import numpy as np
from PIL import Image, ImageFilter
from typing import Dict, Any, Optional
from dotenv import load_dotenv
load_dotenv()

def denoise_image(input_path: str, output_path: str = None,
                  method: str = "bilateral", strength: float = 0.5,
                  preserve_edges: bool = True, output_format: str = "jpg"):
    """
    Remove noise from an image.
    
    Parameters:
    - input_path (str): Path to input image file
    - output_path (str): Path for output file (optional, auto-generated if not provided)
    - method (str): Denoising method ("bilateral", "gaussian", "median", "nlm")
    - strength (float): Denoising strength (0.0-1.0)
    - preserve_edges (bool): Whether to preserve edges during denoising
    - output_format (str): Output image format ("jpg", "png", "tiff")
    
    Returns:
    - dict: Denoising result information
    """
    
    try:
        # Validate parameters
        if not input_path or not os.path.exists(input_path):
            return {"error": "Input image file not found"}
        
        if method not in ["bilateral", "gaussian", "median", "nlm"]:
            return {"error": "Method must be 'bilateral', 'gaussian', 'median', or 'nlm'"}
        
        if strength < 0.0 or strength > 1.0:
            return {"error": "Strength must be between 0.0 and 1.0"}
        
        if output_format not in ["jpg", "png", "tiff"]:
            return {"error": "Output format must be 'jpg', 'png', or 'tiff'"}
        
        # Set output path if not provided
        if not output_path:
            base_name = os.path.splitext(os.path.basename(input_path))[0]
            output_path = f"{base_name}_denoised.{output_format}"
        
        # Load image
        image = cv2.imread(input_path)
        if image is None:
            return {"error": "Could not load image"}
        
        original_size = image.shape[:2]
        
        # Apply denoising based on method
        if method == "bilateral":
            result_image = denoise_bilateral(image, strength, preserve_edges)
        elif method == "gaussian":
            result_image = denoise_gaussian(image, strength)
        elif method == "median":
            result_image = denoise_median(image, strength)
        elif method == "nlm":
            result_image = denoise_nlm(image, strength)
        
        # Save result
        cv2.imwrite(output_path, result_image)
        
        # Calculate noise reduction metrics
        noise_reduction = calculate_noise_reduction(image, result_image)
        
        result = {
            "input_file": input_path,
            "output_path": output_path,
            "method": method,
            "strength": strength,
            "preserve_edges": preserve_edges,
            "output_format": output_format,
            "original_size": (original_size[1], original_size[0]),  # (width, height)
            "result_size": (result_image.shape[1], result_image.shape[0]),
            "noise_reduction": noise_reduction,
            "success": True
        }
        
        # Add file information
        if os.path.exists(output_path):
            result["input_size"] = os.path.getsize(input_path)
            result["output_size"] = os.path.getsize(output_path)
            result["compression_ratio"] = round(result["output_size"] / result["input_size"], 3)
        
        return result
        
    except Exception as e:
        return {"error": f"Error denoising image: {str(e)}"}

def denoise_bilateral(image: np.ndarray, strength: float, preserve_edges: bool) -> np.ndarray:
    """Apply bilateral filtering for edge-preserving denoising."""
    # Calculate parameters based on strength
    d = int(5 + strength * 10)  # Diameter of pixel neighborhood
    sigma_color = 50 + strength * 100  # Filter sigma in the color space
    sigma_space = 50 + strength * 100  # Filter sigma in the coordinate space
    
    if not preserve_edges:
        sigma_color *= 2
        sigma_space *= 2
    
    return cv2.bilateralFilter(image, d, sigma_color, sigma_space)

def denoise_gaussian(image: np.ndarray, strength: float) -> np.ndarray:
    """Apply Gaussian filtering for denoising."""
    # Calculate kernel size based on strength
    kernel_size = int(3 + strength * 10)
    if kernel_size % 2 == 0:
        kernel_size += 1  # Ensure odd kernel size
    
    sigma = strength * 3.0
    
    return cv2.GaussianBlur(image, (kernel_size, kernel_size), sigma)

def denoise_median(image: np.ndarray, strength: float) -> np.ndarray:
    """Apply median filtering for denoising."""
    # Calculate kernel size based on strength
    kernel_size = int(3 + strength * 8)
    if kernel_size % 2 == 0:
        kernel_size += 1  # Ensure odd kernel size
    
    return cv2.medianBlur(image, kernel_size)

def denoise_nlm(image: np.ndarray, strength: float) -> np.ndarray:
    """Apply Non-Local Means denoising."""
    # Convert to float32 for processing
    image_float = image.astype(np.float32) / 255.0
    
    # Calculate parameters based on strength
    h = 0.1 + strength * 0.2  # Filter strength
    template_window_size = 7
    search_window_size = 21
    
    # Apply Non-Local Means
    denoised = cv2.fastNlMeansDenoisingColored(
        image_float, 
        None, 
        h, 
        h, 
        template_window_size, 
        search_window_size
    )
    
    # Convert back to uint8
    return (denoised * 255).astype(np.uint8)

def calculate_noise_reduction(original: np.ndarray, denoised: np.ndarray) -> Dict[str, float]:
    """Calculate noise reduction metrics."""
    try:
        # Convert to grayscale for analysis
        if len(original.shape) == 3:
            original_gray = cv2.cvtColor(original, cv2.COLOR_BGR2GRAY)
            denoised_gray = cv2.cvtColor(denoised, cv2.COLOR_BGR2GRAY)
        else:
            original_gray = original
            denoised_gray = denoised
        
        # Calculate standard deviation (noise indicator)
        original_std = np.std(original_gray)
        denoised_std = np.std(denoised_gray)
        
        # Calculate noise reduction percentage
        noise_reduction_pct = ((original_std - denoised_std) / original_std * 100) if original_std > 0 else 0
        
        # Calculate PSNR (Peak Signal-to-Noise Ratio)
        mse = np.mean((original_gray.astype(float) - denoised_gray.astype(float)) ** 2)
        psnr = 20 * np.log10(255.0 / np.sqrt(mse)) if mse > 0 else float('inf')
        
        return {
            "noise_reduction_percent": round(noise_reduction_pct, 2),
            "original_std": round(original_std, 2),
            "denoised_std": round(denoised_std, 2),
            "psnr": round(psnr, 2) if psnr != float('inf') else 0
        }
        
    except Exception as e:
        return {
            "noise_reduction_percent": 0,
            "original_std": 0,
            "denoised_std": 0,
            "psnr": 0
        }

if __name__ == "__main__":
    # Example usage
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    result = denoise_image("./image_data/cat.gif", method="gaussian", strength=0.7, output_format='png')
    print(json.dumps(result, indent=2)) 