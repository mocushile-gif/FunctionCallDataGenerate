import os
import json
import requests
from typing import Optional, Dict, Any
from dotenv import load_dotenv
load_dotenv()

def get_random_images(query: Optional[str] = None,
                      count: int = 1,
                      color: Optional[str] = None,
                      orientation: Optional[str] = None,
                      output_path: Optional[str] = None,
                      download_dir: Optional[str] = None) -> Any:
    """
    Get random images using the Unsplash API.

    Parameters:
    - query (str): Search term / category
    - count (int): Number of images to retrieve (1–30)
    - color (str): Filter by color. Valid values are: black_and_white, black, white, yellow, orange, red, purple, magenta, green, teal, and blue.
    - orientation (str): landscape / portrait / squarish
    - output_path (str): Path to save results JSON
    - download_dir (str): Directory to save downloaded images

    Returns:
    - list[dict]: image metadata list
    """

    if not (1 <= count <= 30):
        return {"error": "Count must be between 1 and 30"}

    api_key = os.environ.get("UNSPLASH_API_KEY")
    headers = {"Accept-Version": "v1"}

    try:
        # 构造请求参数
        if query:
            url = "https://api.unsplash.com/search/photos"
            params = {
                "client_id": api_key,
                "query": query,
                "per_page": count,
                "color": color,
                "orientation": orientation
            }
        else:
            url = "https://api.unsplash.com/photos/random"
            params = {
                "client_id": api_key,
                "count": count,
                "orientation": orientation
            }
            if color:
                params["color"] = color

        response = requests.get(url, headers=headers, params={k: v for k, v in params.items() if v}, timeout=10)
        response.raise_for_status()

        data = response.json()
        # 统一结构
        result = data["results"] if isinstance(data, dict) and "results" in data else (data if isinstance(data, list) else [data])

        simplified_results = []
        for img in result:
            simplified_results.append({
                "id": img.get("id"),
                "description": img.get("alt_description") or img.get("description"),
                "width": img.get("width"),
                "height": img.get("height"),
                "color": img.get("color"),
                "author": img.get("user", {}).get("name"),
                "url": img.get("urls", {}).get("regular"),
                "page": img.get("links", {}).get("html")
            })

        # 处理下载路径
        if download_dir:    
            os.makedirs(download_dir, exist_ok=True)

        for item in simplified_results:
            try:
                image_url = item["url"]
                image_id = item["id"]
                file_path = os.path.join(download_dir, f"image_{image_id}.jpg")
                img_data = requests.get(image_url, timeout=10).content
                with open(file_path, 'wb') as img_file:
                    img_file.write(img_data)
                item["local_path"] = file_path
            except Exception as e:
                item["local_path"] = None
                print(f"⚠️ Failed to download image {item['id']}: {e}")

        if output_path:
            try:
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(simplified_results, f, indent=2, ensure_ascii=False)
            except Exception as e:
                print(f"⚠️ Could not save JSON file: {e}")

        return simplified_results

    except requests.exceptions.RequestException as e:
        return {"error": f"Network error: {str(e)}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}


if __name__ == "__main__":
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    result = get_random_images(
        query="nature",
        count=3,
        orientation="landscape",
        color="green",
        output_path="nature_images.json",
        download_dir="downloaded_images"
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
