import requests
import json
import os
from typing import Optional, List
from dotenv import load_dotenv
load_dotenv()

def get_random_cat_images_info(limit: Optional[int] = None, page: Optional[int] = None, 
                   order: Optional[str] = None, has_breeds: Optional[bool] = None,
                   breed_ids: Optional[List[int]] = None, category_ids: Optional[List[int]] = None,
                   save_to: Optional[str] = None):
    """
    Get random cat images from the Cat API.
    
    Parameters:
    - limit (int, optional): Number of results to return (1-25)
    - page (int, optional): Page number for pagination
    - order (str, optional): Sort order ('ASC', 'DESC', 'RAND')
    - has_breeds (bool, optional): Filter images that have breed data
    - breed_ids (list, optional): Filter by breed IDs
    - category_ids (list, optional): Filter by category IDs
    - save_to (str, optional): File path to save the result as JSON
    
    Returns:
    - dict: Images data or error information
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
            if limit < 1 or limit > 25:
                return {"error": "Limit must be between 1 and 25 for images"}
            params["limit"] = limit
        if page is not None:
            if page < 0:
                return {"error": "Page must be 0 or greater"}
            params["page"] = page
        if order is not None:
            if order not in ["ASC", "DESC", "RAND"]:
                return {"error": "Order must be one of: ASC, DESC, RAND"}
            params["order"] = order
        if has_breeds is not None:
            params["has_breeds"] = has_breeds
        if breed_ids is not None:
            params["breed_ids"] = ",".join(map(str, breed_ids))
        if category_ids is not None:
            params["category_ids"] = ",".join(map(str, category_ids))
        
        # Make the request
        url = f"{base_url}/images/search"
        response = requests.get(url, headers=headers, params=params, timeout=30)
        
        # Handle response
        if response.status_code == 200:
            try:
                data = response.json()
                result = {
                    "operation": "get_cat_images",
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
                        os.makedirs(os.path.dirname(save_to), exist_ok=True)
                        
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
                    "operation": "get_cat_images",
                    "status_code": response.status_code,
                    "data": response.text,
                    "url": response.url,
                    "success": True,
                    "note": "Response is not JSON format"
                }
                
                # Save to file if save_to is provided
                if save_to:
                    try:
                        os.makedirs(os.path.dirname(save_to) or '.', exist_ok=True)
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
                "operation": "get_cat_images",
                "status_code": response.status_code,
                "note": "Some operations require an API key. Get one at https://thecatapi.com/"
            }
        else:
            return {
                "error": f"API request failed with status code {response.status_code}",
                "operation": "get_cat_images",
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
    # Example usage
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    result = get_random_cat_images_info(limit=25, order="RAND", save_to="./cat_images_result.json")
    print(json.dumps(result, indent=2, ensure_ascii=False)) 