import os
import json
import base64
from PIL import Image
import requests
from typing import Optional, Dict, Any
from dotenv import load_dotenv
load_dotenv()

def describe_image(image_path, max_tokens=300, 
                   detail_level="auto", language="en", include_metadata=True):
    """
    Generate a detailed description of an image using Zhipu AI GLM-4V vision models.
    
    Args:
        image_path (str): Path to the input image file
        max_tokens (int): Maximum number of tokens for the description
        detail_level (str): Detail level - "low", "high", "auto"
        language (str): Language for the description
        include_metadata (bool): Whether to include image metadata
    
    Returns:
        dict: Result information including success status and description
    """
    try:
        # Validate input file
        if not os.path.exists(image_path):
            return {
                "success": False,
                "error": f"Image file not found: {image_path}"
            }
        
        # Get image metadata
        metadata = {}
        if include_metadata:
            try:
                with Image.open(image_path) as img:
                    metadata = {
                        "format": img.format,
                        "mode": img.mode,
                        "size": f"{img.width}x{img.height}",
                        "width": img.width,
                        "height": img.height
                    }
                    
                    # Get file size
                    file_size = os.path.getsize(image_path)
                    metadata["file_size_bytes"] = file_size
                    metadata["file_size_mb"] = round(file_size / (1024 * 1024), 2)
                    
            except Exception as e:
                metadata["error"] = f"Failed to get metadata: {str(e)}"
        
        # Try different description methods
        description_result = _try_zhipu_vision(image_path, max_tokens, detail_level, language)
        
        # Combine results
        result = {
            "success": True,
            "image_path": image_path,
            "language": language,
            "description": description_result.get("description", ""),
        }
        
        if include_metadata:
            result["metadata"] = metadata
        
        if description_result.get("tags"):
            result["tags"] = description_result["tags"]
        
        if description_result.get("objects"):
            result["objects"] = description_result["objects"]
        
        return result
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Error describing image: {str(e)}"
        }

def _try_zhipu_vision(image_path, max_tokens, detail_level, language):
    """
    Use Zhipu GLM-4V API to describe an image, with prompt dynamically adjusted by detail_level and max_tokens.
    
    Parameters:
    - image_path (str): Path to the image file
    - max_tokens (int): Max response tokens AND used in prompt as soft constraint
    - detail_level (str): One of "low", "high", "auto"
    - language (str): Output language (e.g., "zh", "en", "ja")
    
    Returns:
    - dict: {success: bool, content or error}
    """
    api_key = os.getenv("ZHIPU_API_KEY")
    if not api_key:
        return {"success": False, "error": "ZHIPU_API_KEY not found in environment variables"}

    try:
        with open(image_path, "rb") as f:
            image_base64 = base64.b64encode(f.read()).decode("utf-8")
    except Exception as e:
        return {"success": False, "error": f"Failed to read image: {e}"}

    def build_prompt(detail_level, language, max_tokens):
        token_limit_note = f"（不超过 {max_tokens} 个 token）" if language == "zh" else f"(no more than {max_tokens} tokens)"
        if language == "zh":
            if detail_level == "low":
                return f"请简要描述这张图片的内容。{token_limit_note}"
            elif detail_level == "high":
                return f"请尽可能详细地描述这张图片的内容，包括主要物体、颜色、背景、情绪和任何可见细节。{token_limit_note}"
            else:  # auto
                return f"请描述这张图片的内容，包括主要对象、颜色、构图和显著特征。{token_limit_note}"
        else:
            if detail_level == "low":
                return f"Briefly describe this image. {token_limit_note}"
            elif detail_level == "high":
                return f"Describe this image in as much detail as possible, including objects, colors, background, emotion, and notable features. {token_limit_note}"
            else:
                return f"Please describe this image, focusing on main subjects, color, layout, and key features. {token_limit_note}"

    prompt_text = build_prompt(detail_level, language, max_tokens)

    payload = {
        "model": "glm-4v-flash",
        "max_tokens": max_tokens,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}},
                    {"type": "text", "text": prompt_text}
                ]
            }
        ]
    }

    response = requests.post(
        "https://open.bigmodel.cn/api/paas/v4/chat/completions",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        },
        data=json.dumps(payload)
    )
    result = response.json()
    return {"success": True, "description": result["choices"][0]["message"]["content"]}


if __name__ == "__main__":
    # Test the function
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    result = describe_image(
        image_path="./image_data/dog.jpg",
        max_tokens=100, 
        detail_level="low",
        language="en"
    )
    print(json.dumps(result, indent=2)) 