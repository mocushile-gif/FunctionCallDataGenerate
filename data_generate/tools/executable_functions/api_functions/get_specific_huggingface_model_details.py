import os
import json
import requests
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv
load_dotenv()

def get_specific_huggingface_model_details(model_id: str, save_to: Optional[str] = None):
    """
    Get detailed information about a specific Hugging Face model.

    Parameters:
    - model_id (str): The model ID (e.g., "gpt2", "bert-base-uncased").
    - save_to (str, optional): Path to save the result JSON to a file.

    Returns:
    - dict: Detailed model information.
    - str: Error message if an exception occurs.
    """
    try:
        if not model_id:
            return {"error": "Model ID is required"}
        
        # Get API key from environment
        api_key = os.getenv("HUGGINGFACE_API_KEY")
        
        if not api_key:
            return {"error": "Hugging Face API key not provided. Set HUGGINGFACE_API_KEY environment variable."}
        
        # Prepare API request
        url = f"https://huggingface.co/api/models/{model_id}"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # Make API request
        print(f"Fetching details for model: {model_id}")
        response = requests.get(url, headers=headers)
        # print(response.json())
        if response.status_code != 200:
            return {"error": f"API request failed with status {response.status_code}: {response.text}"}
        
        model_data = response.json()
        
        # Format detailed model information
        model_details = {
            "id": model_data.get("id"),
            "name": model_data.get("modelId"),
            "author": model_data.get("author"),
            "description": model_data.get("description"),
            "tags": model_data.get("tags", []),
            "task": model_data.get("pipeline_tag"),
            "downloads": model_data.get("downloads", 0),
            "likes": model_data.get("likes", 0),
            "updated_at": model_data.get("lastModified"),
            "created_at": model_data.get("createdAt"),
            "language": model_data.get("language"),
            "license": model_data.get("license"),
            "library_name": model_data.get("library_name"),
            "model_type": model_data.get("model_type"),
            "url": f"https://huggingface.co/{model_data.get('id')}",
            "card_data": model_data.get("cardData", {}),
            "siblings": model_data.get("siblings", []),
            "config": model_data.get("config", {}),
            "spaces": model_data.get("spaces", []),
            "datasets": model_data.get("datasets", []),
            "metrics": {
                "downloads": model_data.get("downloads", 0),
                "likes": model_data.get("likes", 0),
                "comments": len(model_data.get("comments", [])),
                "discussions": len(model_data.get("discussions", []))
            }
        }
        
        result = {
            "model_id": model_id,
            "model_details": model_details,
            "success": True
        }
        
        # Save result to file if requested
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
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": f"Failed to get model details: {str(e)}"}

if __name__ == "__main__":
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    details = get_specific_huggingface_model_details(
        model_id="gpt2",
        save_to="./gpt2_details.json"
    )
    print(json.dumps(details, indent=2, ensure_ascii=False)) 