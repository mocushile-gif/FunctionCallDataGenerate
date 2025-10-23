import os
import json
import time
from typing import Dict, Any, Optional
from dotenv import load_dotenv
load_dotenv()

def extract_image_info(image_path: str, include_histogram: bool = False):
    """
    Extract detailed information about an image including metadata and optional histogram.

    Parameters:
    - image_path (str): Path to the input image file.
    - include_histogram (bool): Whether to include color histogram. Default is False.

    Returns:
    - dict: Image information including metadata, and optional histogram.
    - str: Error message if an exception occurs.
    """
    
    try:
        # Check if input file exists
        if not os.path.exists(image_path):
            return {"error": f"Input image file not found: {image_path}"}
        
        # Get basic file information
        file_size = os.path.getsize(image_path)
        file_ext = os.path.splitext(image_path)[1].lower()
        file_name = os.path.basename(image_path)
        file_dir = os.path.dirname(image_path)
        
        # Get file modification time
        mod_time = os.path.getmtime(image_path)
        mod_time_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(mod_time))
        
        # Initialize result
        result = {
            "file_info": {
                "path": image_path,
                "name": file_name,
                "directory": file_dir,
                "extension": file_ext,
                "size_bytes": file_size,
                "size_mb": round(file_size / (1024 * 1024), 2),
                "modified_time": mod_time_str,
                "modified_timestamp": mod_time
            }
        }
        
        # Check if PIL is available for detailed image analysis
        try:
            from PIL import Image
            
            # Open the image
            with Image.open(image_path) as img:
                # Basic image information
                result["image_info"] = {
                    "format": img.format,
                    "mode": img.mode,
                    "size": img.size,
                    "width": img.width,
                    "height": img.height,
                    "aspect_ratio": round(img.width / img.height, 3),
                    "total_pixels": img.width * img.height,
                    "megapixels": round((img.width * img.height) / 1000000, 2)
                }
                
                # Color information
                if img.mode in ['RGB', 'RGBA']:
                    result["color_info"] = {
                        "color_mode": img.mode,
                        "channels": len(img.mode),
                        "has_alpha": 'A' in img.mode
                    }
                elif img.mode == 'L':
                    result["color_info"] = {
                        "color_mode": "Grayscale",
                        "channels": 1,
                        "has_alpha": False
                    }
                else:
                    result["color_info"] = {
                        "color_mode": img.mode,
                        "channels": "Unknown",
                        "has_alpha": "Unknown"
                    }
                
                # Color histogram
                if include_histogram:
                    try:
                        # Convert to RGB for histogram analysis
                        if img.mode != 'RGB':
                            rgb_img = img.convert('RGB')
                        else:
                            rgb_img = img
                        
                        # Get histogram
                        histogram = rgb_img.histogram()
                        
                        # Separate R, G, B histograms
                        r_hist = histogram[:256]
                        g_hist = histogram[256:512]
                        b_hist = histogram[512:768]
                        
                        # Calculate basic statistics
                        def get_stats(hist):
                            total = sum(hist)
                            if total == 0:
                                return {"mean": 0, "std": 0, "min": 0, "max": 0}
                            
                            mean = sum(i * count for i, count in enumerate(hist)) / total
                            variance = sum((i - mean) ** 2 * count for i, count in enumerate(hist)) / total
                            std = variance ** 0.5
                            
                            # Find min and max (non-zero values)
                            non_zero = [i for i, count in enumerate(hist) if count > 0]
                            min_val = min(non_zero) if non_zero else 0
                            max_val = max(non_zero) if non_zero else 0
                            
                            return {
                                "mean": round(mean, 2),
                                "std": round(std, 2),
                                "min": min_val,
                                "max": max_val,
                                "total_pixels": total
                            }
                        
                        result["histogram"] = {
                            "red": get_stats(r_hist),
                            "green": get_stats(g_hist),
                            "blue": get_stats(b_hist)
                        }
                        
                    except Exception as e:
                        result["histogram"] = {"error": f"Failed to calculate histogram: {str(e)}"}
                else:
                    result["histogram"] = None
                
                
        except ImportError:
            # PIL not available, return basic file info only
            result["note"] = "PIL/Pillow not available - only basic file information is provided. Install PIL for detailed image analysis."
            result["image_info"] = None
            result["color_info"] = None
            result["histogram"] = None
        
        except Exception as e:
            result["error"] = f"Image analysis failed: {str(e)}"
        
        # Add success flag
        result["success"] = "error" not in result

        return result
        
    except Exception as e:
        return {"error": f"Image info extraction failed: {str(e)}"}

if __name__ == "__main__":
    # Example usage
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    result = extract_image_info(
        image_path="./image_data/cat.gif",
        include_histogram=True
    )
    print(json.dumps(result, indent=2, ensure_ascii=False)) 