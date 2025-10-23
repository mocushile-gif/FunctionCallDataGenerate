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

def upload_image_to_url(image_path):
    """
    Upload a local image to a free image hosting service and return the public URL.
    
    Args:
        image_path (str): Path to the local image file
    
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

def _upload_to_imgur(image_path):
    """Upload image to Imgur (requires client ID)."""
    try:
        # Imgur API endpoint
        url = "https://api.imgur.com/3/image"
        
        # Use default client ID if none provided
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

def detect_image_objects(
    image: str,
    save_result: Optional[str] = None
) -> dict:
    """
    Detect objects in an image via RapidAPI, supports both local file path or remote URL.

    Parameters:
    - image (str): Local path or remote URL of the image.
    - save_result (str, optional): Path to save JSON result.

    Returns:
    - dict: Detection result.
    """
    # Determine if image is a URL or local file
    if image.startswith("http://") or image.startswith("https://"):
        image_url = image
        print(f"✅ Using remote image URL: {image_url}")
    elif os.path.exists(image):
        upload_result = upload_image_to_url(image)
        if upload_result['success']:
            image_url=upload_result['image_url']
        else:
            return {"success": False, "error": "Failed to upload local image"}
        print(f"✅ Uploaded local image to: {image_url}")
    else:
        return {"success": False, "error": f"Invalid image path or URL: {image}"}

    # Call RapidAPI
    url = "https://general-image-detection.p.rapidapi.com/"
    headers = {
        "x-rapidapi-key": os.getenv("RAPID_API_KEY"),
        "x-rapidapi-host": "general-image-detection.p.rapidapi.com",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    payload = f"image_url={image_url}"

    try:
        response = requests.post(url, data=payload, headers=headers)
        response.raise_for_status()
        result = response.json()

        final_result = {
            "success": True,
            "image_url": image_url,
            "result": result
        }

        if save_result:
            os.makedirs(os.path.dirname(save_result), exist_ok=True)
            with open(save_result, "w", encoding="utf-8") as f:
                json.dump(final_result, f, indent=2, ensure_ascii=False)

        return final_result

    except Exception as e:
        return {"success": False, "error": f"API request failed: {e}"}


if __name__ == "__main__":
    # 可传入本地路径或远程 URL
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    image_input = "./image_data/dog.jpg"  # 本地图片
    # image_input = "https://i.imgur.com/IEygXiv.jpeg"  # 远程图片

    result = detect_image_objects(
        image=image_input,
    )

    print(json.dumps(result, indent=2, ensure_ascii=False))
