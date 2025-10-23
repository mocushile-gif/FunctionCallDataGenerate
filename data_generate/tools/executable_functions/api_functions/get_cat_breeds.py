import requests
import json
import os
from typing import Optional
from dotenv import load_dotenv
load_dotenv()

def get_cat_breeds(limit: Optional[int] = None, page: Optional[int] = None, 
                   save_to: Optional[str] = None):
    """
    Get all cat breeds from the Cat API.
    
    Parameters:
    - limit (int, optional): Number of results to return (1-100)
    - page (int, optional): Page number for pagination
    - save_to (str, optional): File path to save the result as JSON
    
    Returns:
    - dict: Breeds data or error information
    """
    # API base URL
    base_url = "https://api.thecatapi.com/v1"
    
    # API key from environment
    api_key = os.getenv("CAT_API_KEY")
    
    # Headers
    headers = {
        "Content-Type": "application/json"
    }
    if api_key:
        headers["x-api-key"] = api_key
    
    try:
        # Build request parameters
        params = {}
        if limit is not None:
            if limit < 1 or limit > 100:
                return {"error": "Limit must be between 1 and 100"}
            params["limit"] = limit
        if page is not None:
            if page < 0:
                return {"error": "Page must be 0 or greater"}
            params["page"] = page
        
        # Make the request
        url = f"{base_url}/breeds"
        response = requests.get(url, headers=headers, params=params, timeout=30)
        
        # Handle response
        if response.status_code == 200:
            try:
                data = response.json()
                result = {
                    "operation": "get_cat_breeds",
                    "status_code": response.status_code,
                    "data": data,
                    "url": response.url,
                    "count": len(data),
                    "success": True
                }
                
                # Save to file if save_to is provided
                if save_to:
                    try:
                        # Ensure directory exists
                        os.makedirs(os.path.dirname(save_to) or '.', exist_ok=True)
                        
                        # Save the result to file
                        with open(save_to, 'w', encoding='utf-8') as f:
                            json.dump(result, f, indent=2, ensure_ascii=False)
                        
                        result["saved_to"] = save_to
                        result["save_success"] = True
                    except Exception as save_error:
                        result["save_error"] = str(save_error)
                        result["save_success"] = False
                
                return result
            except json.JSONDecodeError:
                result = {
                    "operation": "get_cat_breeds",
                    "status_code": response.status_code,
                    "data": response.text,
                    "url": response.url,
                    "success": True,
                    "note": "Response is not JSON format"
                }
                
                # Save to file if save_to is provided
                if save_to:
                    try:
                        os.makedirs(os.path.dirname(save_to), exist_ok=True)
                        with open(save_to, 'w', encoding='utf-8') as f:
                            json.dump(result, f, indent=2, ensure_ascii=False)
                        result["saved_to"] = save_to
                        result["save_success"] = True
                    except Exception as save_error:
                        result["save_error"] = str(save_error)
                        result["save_success"] = False
                
                return result
        elif response.status_code == 401:
            return {
                "error": "Unauthorized - API key may be required or invalid",
                "operation": "get_cat_breeds",
                "status_code": response.status_code,
                "note": "Some operations require an API key. Get one at https://thecatapi.com/"
            }
        else:
            return {
                "error": f"API request failed with status code {response.status_code}",
                "operation": "get_cat_breeds",
                "status_code": response.status_code,
                "url": response.url,
                "response_text": response.text
            }
            
    except requests.exceptions.Timeout:
        return {"error": "Request timeout"}
    except requests.exceptions.ConnectionError:
        return {"error": "Connection error - unable to reach the API"}
    except requests.exceptions.RequestException as e:
        return {"error": f"Request failed: {str(e)}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}

if __name__ == "__main__":
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    # Example usage
    result = get_cat_breeds(limit=100, save_to="./cat_breeds_result.json")
    print(json.dumps(result, indent=2, ensure_ascii=False)) 