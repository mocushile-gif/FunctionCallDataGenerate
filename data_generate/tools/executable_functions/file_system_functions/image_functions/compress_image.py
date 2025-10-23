import os
import json
from typing import Dict, Any, Optional
from dotenv import load_dotenv
load_dotenv()

def compress_image(image_path: str, quality: int = 85, max_width: Optional[int] = None,
                  max_height: Optional[int] = None, output_format: str = "JPEG",
                  output_path: Optional[str] = None):
    """
    Compress image by reducing quality and/or size while maintaining visual quality.

    Parameters:
    - image_path (str): Path to the input image file.
    - quality (int): JPEG quality (1-100). Higher values mean better quality but larger file size.
    - max_width (int, optional): Maximum width in pixels. If provided, image will be resized.
    - max_height (int, optional): Maximum height in pixels. If provided, image will be resized.
    - output_format (str): Output format (JPEG, PNG, WEBP). Default is JPEG.
    - output_path (str, optional): Path for the output image. If not provided, will create compressed version.

    Returns:
    - dict: Compression result information.
    - str: Error message if an exception occurs.
    """
    
    
    try:
        # Check if input file exists
        if not os.path.exists(image_path):
            return {"error": f"Input image file not found: {image_path}"}
        
        # Validate quality
        if quality < 1 or quality > 100:
            return {"error": "Quality must be between 1 and 100"}
        
        # Validate output format
        valid_formats = ["JPEG", "PNG", "WEBP"]
        if output_format.upper() not in valid_formats:
            return {"error": f"Output format must be one of: {valid_formats}"}
        
        # Set output path if not provided
        if output_path is None:
            base_name = os.path.splitext(image_path)[0]
            ext = "." + output_format.lower()
            output_path = f"{base_name}_compressed{ext}"
        
        # Get file information
        input_file_size = os.path.getsize(image_path)
        input_file_ext = os.path.splitext(image_path)[1].lower()
        
        # Check if PIL is available for actual image processing
        try:
            from PIL import Image
            
            # Open the image
            with Image.open(image_path) as img:
                original_size = img.size
                original_mode = img.mode
                
                # Resize if max dimensions are provided
                if max_width or max_height:
                    # Calculate new size maintaining aspect ratio
                    width, height = img.size
                    if max_width and max_height:
                        # Scale down to fit within both dimensions
                        scale = min(max_width / width, max_height / height)
                        new_width = int(width * scale)
                        new_height = int(height * scale)
                    elif max_width:
                        # Scale down to fit width
                        scale = max_width / width
                        new_width = max_width
                        new_height = int(height * scale)
                    else:
                        # Scale down to fit height
                        scale = max_height / height
                        new_width = int(width * scale)
                        new_height = max_height
                    
                    img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                # Prepare save parameters
                save_params = {}
                if output_format.upper() == "JPEG":
                    save_params["quality"] = quality
                    save_params["optimize"] = True
                elif output_format.upper() == "PNG":
                    save_params["optimize"] = True
                elif output_format.upper() == "WEBP":
                    save_params["quality"] = quality
                    save_params["method"] = 6  # Best compression
                
                # Save the compressed image
                img.save(output_path, format=output_format.upper(), **save_params)
                
                # Get output file information
                output_file_size = os.path.getsize(output_path)
                compression_ratio = (1 - output_file_size / input_file_size) * 100
                
                result = {
                    "input_path": image_path,
                    "output_path": output_path,
                    "quality": quality,
                    "max_width": max_width,
                    "max_height": max_height,
                    "output_format": output_format.upper(),
                    "original_size": original_size,
                    "compressed_size": img.size,
                    "original_mode": original_mode,
                    "compressed_mode": img.mode,
                    "input_file_size": input_file_size,
                    "output_file_size": output_file_size,
                    "compression_ratio": round(compression_ratio, 2),
                    "size_reduction_mb": round((input_file_size - output_file_size) / (1024 * 1024), 2),
                    "success": True
                }
                
        except ImportError:
            # PIL not available, return mock result
            result = {
                "input_path": image_path,
                "output_path": output_path,
                "quality": quality,
                "max_width": max_width,
                "max_height": max_height,
                "output_format": output_format.upper(),
                "input_file_size": input_file_size,
                "file_extension": input_file_ext,
                "success": True,
                "note": "PIL/Pillow not available - this is a mock result. Install PIL for actual image compression."
            }
        
        except Exception as e:
            return {"error": f"Image compression failed: {str(e)}"}
        
        return result
        
    except Exception as e:
        return {"error": f"Image compression failed: {str(e)}"}

if __name__ == "__main__":
    # Example usage
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    result = compress_image(
        image_path="./image_data/dog.jpg",
        quality=80,
        max_width=800,
        max_height=600,
        output_format="JPEG",
        output_path="./compressed_image.jpg",
    )
    print(json.dumps(result, indent=2, ensure_ascii=False)) 