import requests
import json
from typing import Dict, Any, Optional
from dotenv import load_dotenv
load_dotenv()

def http_request(url: str, method: str = "GET", headers: Optional[Dict[str, str]] = None, 
                data: Optional[Dict[str, Any]] = None, timeout: int = 30):
    """
    Send HTTP request to the specified URL.

    Parameters:
    - url (str): The URL to send the request to.
    - method (str): HTTP method (GET, POST, PUT, DELETE, etc.). Default is "GET".
    - headers (dict, optional): Request headers.
    - data (dict, optional): Request data for POST/PUT requests.
    - timeout (int): Request timeout in seconds. Default is 30.

    Returns:
    - dict: Response information including status_code, headers, and content.
    - str: Error message if an exception occurs.
    """
    try:
        # Prepare request parameters
        request_params = {
            "method": method.upper(),
            "url": url,
            "timeout": timeout
        }
        
        # Add headers if provided
        if headers:
            request_params["headers"] = headers
        
        # Add data for POST/PUT requests
        if data and method.upper() in ["POST", "PUT", "PATCH"]:
            request_params["json"] = data
        
        # Send the request
        response = requests.request(**request_params)
        
        # Prepare response data
        response_data = {
            "url": url,
            "method": method.upper(),
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "content_type": response.headers.get("content-type", ""),
            "content_length": len(response.content)
        }
        
        # Handle response content
        try:
            # Try to parse as JSON
            if "application/json" in response.headers.get("content-type", ""):
                response_data["content"] = response.json()
                response_data["content_type_parsed"] = "json"
            else:
                # Return text content (truncated if too long)
                content = response.text
                if len(content) > 1000:
                    content = content[:1000] + "... (truncated)"
                response_data["content"] = content
                response_data["content_type_parsed"] = "text"
        except Exception as e:
            # If JSON parsing fails, return text content
            content = response.text
            if len(content) > 1000:
                content = content[:1000] + "... (truncated)"
            response_data["content"] = content
            response_data["content_type_parsed"] = "text"
            response_data["parse_error"] = str(e)
        
        return response_data
        
    except requests.exceptions.Timeout:
        return {"error": f"Request timeout after {timeout} seconds"}
    except requests.exceptions.ConnectionError:
        return {"error": "Connection error - unable to reach the server"}
    except requests.exceptions.RequestException as e:
        return {"error": f"Request failed: {str(e)}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}

if __name__ == "__main__":
    # Example usage
    result = http_request("https://httpbin.org/json")
    print(json.dumps(result, indent=2, ensure_ascii=False)) 