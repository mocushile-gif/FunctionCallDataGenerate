import os
import json
import base64
import requests
from PIL import Image
from typing import Optional, Dict, Any, List
import mimetypes
import time
from dotenv import load_dotenv
load_dotenv()

def upload_image_to_url(image_path: str, max_size_mb: int = 32, compress_quality: int = 85):
    """
    Upload a local image to a free image hosting service and return the public URL.
    
    Args:
        image_path (str): Path to the local image file
        max_size_mb (int): Maximum file size in MB before compression
        compress_quality (int): JPEG compression quality (1-100)
    
    Returns:
        dict: Result information including success status and image URL
    """
    try:
        # Validate input file
        if not os.path.exists(image_path):
            return {
                "success": False,
                "error": f"Image file not found: {image_path}"
            }
        
        # Get file info
        file_size = os.path.getsize(image_path)
        file_size_mb = file_size / (1024 * 1024)
        
        # Check if compression is needed
        if file_size_mb > max_size_mb:
            image_path = _compress_image(image_path, max_size_mb, compress_quality)
            if not image_path:
                return {
                    "success": False,
                    "error": "Failed to compress image"
                }
        
        # Try different upload services
        upload_result = None
        
        upload_result = _upload_to_imgur(image_path)
        
        if upload_result and upload_result["success"]:
            return {
                "success": True,
                "image_url": upload_result["url"],
                "delete_url": upload_result.get("delete_url"),
                "original_path": image_path,
                "file_size_mb": round(file_size_mb, 2)
            }
        else:
            return {
                "success": False,
                "error": upload_result.get("error", "All upload services failed")
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": f"Error uploading image: {str(e)}"
        }

def _compress_image(image_path, max_size_mb, quality):
    """Compress image to meet size requirements."""
    try:
        with Image.open(image_path) as img:
            # Convert to RGB if necessary
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')
            
            # Calculate target size
            target_size = max_size_mb * 1024 * 1024
            
            # Start with original quality
            current_quality = quality
            
            # Create temporary file path
            temp_path = f"{image_path}_compressed.jpg"
            
            while current_quality > 10:
                img.save(temp_path, 'JPEG', quality=current_quality, optimize=True)
                
                if os.path.getsize(temp_path) <= target_size:
                    return temp_path
                
                current_quality -= 10
            
            # If still too large, resize the image
            width, height = img.size
            scale_factor = 0.9
            
            while scale_factor > 0.3:
                new_width = int(width * scale_factor)
                new_height = int(height * scale_factor)
                
                resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                resized_img.save(temp_path, 'JPEG', quality=quality, optimize=True)
                
                if os.path.getsize(temp_path) <= target_size:
                    return temp_path
                
                scale_factor -= 0.1
            
            return None
            
    except Exception as e:
        print(f"Compression error: {e}")
        return None

def _upload_to_imgur(image_path, client_id=None):
    """Upload image to Imgur (requires client ID)."""
    try:
        # Imgur API endpoint
        url = "https://api.imgur.com/3/image"
        
        # Use default client ID if none provided
        if not client_id:
            client_id = "546c25a59c58ad7"  # Example client ID, replace with real one
        
        headers = {
            'Authorization': f'Client-ID {client_id}'
        }
        
        with open(image_path, 'rb') as file:
            files = {'image': file}
            response = requests.post(url, headers=headers, files=files, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    return {
                        "success": True,
                        "url": result['data']['link'],
                        "delete_url": f"https://imgur.com/delete/{result['data']['deletehash']}",
                        "service": "imgur"
                    }
            
            return {
                "success": False,
                "error": f"Imgur upload failed: {response.status_code}"
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": f"Imgur error: {str(e)}"
        }

if __name__ == "__main__":
    # Test the function
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    result = upload_image_to_url(
        image_path="./image_data/dog.jpg"
    )
    print(json.dumps(result, indent=2)) 