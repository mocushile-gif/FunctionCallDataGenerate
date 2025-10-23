import os
import json
import requests
import time
from typing import Dict, Any, Optional
from urllib.parse import urlparse
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

def download_image(url: str, output_path: Optional[str] = None, 
                  timeout: int = 30, verify_ssl: bool = True,
                  headers: Optional[Dict[str, str]] = None):
    """
    Download image from URL and save to local file.

    Parameters:
    - url (str): URL of the image to download.
    - output_path (str, optional): Path to save the downloaded image. If not provided, will use filename from URL.
    - timeout (int): Request timeout in seconds. Default is 30.
    - verify_ssl (bool): Whether to verify SSL certificates. Default is True.
    - headers (dict, optional): Custom headers for the request.

    Returns:
    - dict: Download result information.
    - str: Error message if an exception occurs.
    """
    
    
    try:
        # Validate URL
        if not url or not url.startswith(('http://', 'https://')):
            return {"error": "Invalid URL. Must start with http:// or https://"}
        
        # Parse URL to get filename
        parsed_url = urlparse(url)
        original_filename = os.path.basename(parsed_url.path)
        
        # Set output path if not provided
        if output_path is None:
            if original_filename and '.' in original_filename:
                # Use original filename
                timestamp = int(time.time())
                name, ext = os.path.splitext(original_filename)
                output_path = f"./downloaded_images/{name}_{timestamp}{ext}"
            else:
                # Generate filename based on URL
                timestamp = int(time.time())
                output_path = f"./downloaded_images/downloaded_image_{timestamp}.jpg"
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Set default headers if not provided
        if headers is None:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
        
        # Download the image
        print(f"Downloading image from: {url}")
        response = requests.get(
            url, 
            timeout=timeout, 
            verify=verify_ssl, 
            headers=headers,
            stream=True
        )
        response.raise_for_status()
        
        # Check if response is actually an image
        content_type = response.headers.get('content-type', '').lower()
        if not content_type.startswith('image/'):
            return {"error": f"URL does not point to an image. Content-Type: {content_type}"}
        
        # Get file size from headers
        file_size = int(response.headers.get('content-length', 0))
        
        # Save the image
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        
        # Verify file was saved and get actual size
        actual_size = os.path.getsize(output_path)
        
        # Get file extension
        file_ext = os.path.splitext(output_path)[1].lower()
        
        # Determine image format
        image_format = file_ext[1:] if file_ext else 'unknown'
        
        result = {
            "url": url,
            "output_path": output_path,
            "original_filename": original_filename,
            "file_size": actual_size,
            "expected_size": file_size,
            "content_type": content_type,
            "image_format": image_format,
            "timeout": timeout,
            "verify_ssl": verify_ssl,
            "success": True
        }
        
        return result
        
    except requests.exceptions.Timeout:
        return {"error": f"Download timeout after {timeout} seconds"}
    except requests.exceptions.ConnectionError:
        return {"error": "Connection error. Please check your internet connection and the URL."}
    except requests.exceptions.HTTPError as e:
        return {"error": f"HTTP error: {e.response.status_code} - {e.response.reason}"}
    except requests.exceptions.RequestException as e:
        return {"error": f"Request error: {str(e)}"}
    except Exception as e:
        return {"error": f"Download failed: {str(e)}"}

if __name__ == "__main__":
    # Example usage
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    result = download_image(
        url="https://cdn2.thecatapi.com/images/MTczOTM3NQ.gif",
        output_path="./test_download.jpg",
    )
    print(json.dumps(result, indent=2, ensure_ascii=False)) 