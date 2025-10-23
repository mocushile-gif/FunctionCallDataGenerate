import os
import json
import time
import requests
from typing import Optional, Tuple
from dotenv import load_dotenv
load_dotenv()

def parse_and_validate_size(size_str: str) -> Tuple[int, int]:
    """
    Parse and validate size string like '1024x1024' and return (width, height).
    Raises ValueError if invalid.
    """
    try:
        width, height = map(int, size_str.lower().split('x'))
    except Exception:
        raise ValueError("Size must be in 'widthxheight' format, e.g., '1024x1024'.")

    if not (512 <= width <= 2048 and 512 <= height <= 2048):
        raise ValueError("Width and height must be between 512 and 2048 pixels.")

    if width % 16 != 0 or height % 16 != 0:
        raise ValueError("Width and height must be divisible by 16.")

    if width * height > 2 ** 21:
        raise ValueError("Image resolution exceeds maximum allowed pixel count (2^21).")

    return width, height


def generate_image(prompt: str,
                         size: str = "1024x1024",
                         output_path: Optional[str] = None) -> dict:
    """
    Generate image using Zhipu BigModel Image Generation API.

    Parameters:
    - prompt (str): Prompt for the image generation
    - size (str): Image size in 'widthxheight' format. Default is '1024x1024'.
    - output_path (str, optional): Local path to save the image

    Returns:
    - dict: Metadata of the image generation result
    """
    # Output path setup
    if output_path is None:
        timestamp = int(time.time())
        output_path = f"./generated_images/image_{timestamp}.png"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # API key
    token = os.environ.get("ZHIPU_API_KEY", "")
    if not token:
        return {"error": "ZHIPU_API_KEY not found in environment."}

    # Validate size
    try:
        width, height = parse_and_validate_size(size)
    except ValueError as ve:
        return {"error": str(ve)}

    # API call
    try:
        url = "https://open.bigmodel.cn/api/paas/v4/images/generations"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "cogview-3-flash",
            "prompt": prompt,
            "size": size
        }

        response = requests.post(url, headers=headers, json=payload, timeout=60)
        print("API response:", response.text)
        response.raise_for_status()
        res_data = response.json()

        if "data" not in res_data or not res_data["data"]:
            return {"error": "No image URL returned", "raw": res_data}

        image_url = res_data["data"][0]["url"]
        image_data = requests.get(image_url, timeout=60).content

        with open(output_path, "wb") as f:
            f.write(image_data)

        return {
            "success": True,
            "model": "cogview-3-flash",
            "prompt": prompt,
            "width": width,
            "height": height,
            "image_url": image_url,
            "output_path": output_path,
            "file_size": os.path.getsize(output_path)
        }

    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    result = generate_image(
        prompt="赛博朋克风格的未来城市，夜晚，霓虹灯",
        size="768x1344"
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
