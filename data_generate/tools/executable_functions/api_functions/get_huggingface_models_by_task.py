import os
import json
import requests
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv
load_dotenv()

def get_huggingface_models_by_task(query: str = "", task: str = "", limit: int = 20, 
                          sort: str = "downloads", direction: int = -1,
                          save_to: Optional[str] = None):
    """
    Get Hugging Face models list with filtering and sorting options.

    Parameters:
    - query (str): Search query to filter models by name or description.
    - task (str): Filter models by specific task (e.g., "text-generation", "image-classification").
    - limit (int): Maximum number of models to return. Default is 20, max is 100.
    - sort (str): Sort order ("downloads", "likes", "updated", "name"). Default is "downloads".
    - direction (int): Sort direction (-1 or 1). Default is -1.
    - save_to (str, optional): Path to save the result JSON to a file.

    Returns:
    - dict: Models list with metadata and statistics.
    - str: Error message if an exception occurs.
    """
    try:
        # Validate parameters
        if limit <= 0 or limit > 100:
            return {"error": "Limit must be between 1 and 100"}
        
        if sort not in ["downloads", "likes", "updated", "name"]:
            return {"error": "Sort must be one of: downloads, likes, updated, name"}
        
        if direction !=-1 and direction!=1:
            return {"error": "Direction must be -1 or 1"}
        
        # Get API key from environment
        api_key = os.getenv("HUGGINGFACE_API_KEY")
        
        if not api_key:
            return {"error": "Hugging Face API key not provided. Set HUGGINGFACE_API_KEY environment variable."}
        
        # Prepare API request
        url = "https://huggingface.co/api/models"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        params = {
            "limit": limit,
            "sort": sort,
            "direction": direction
        }
        
        if query:
            params["search"] = query
        
        if task:
            params["filter"] = task
        
        # Make API request
        print(f"Fetching models with query: '{query}', task: '{task}', limit: {limit}")
        response = requests.get(url, headers=headers, params=params)
        # print(response.json())
        if response.status_code != 200:
            return {"error": f"API request failed with status {response.status_code}: {response.text}"}
        
        models_data = response.json()
        
        # Process and format results
        models = []
        total_downloads = 0
        total_likes = 0
        
        for model in models_data:
            model_info = {
                "id": model.get("id"),
                "name": model.get("modelId"),
                "author": model.get("author"),
                "description": model.get("description"),
                "tags": model.get("tags", []),
                "task": model.get("pipeline_tag"),
                "downloads": model.get("downloads", 0),
                "likes": model.get("likes", 0),
                "updated_at": model.get("lastModified"),
                "created_at": model.get("createdAt"),
                "language": model.get("language"),
                "license": model.get("license"),
                "library_name": model.get("library_name"),
                "model_type": model.get("model_type"),
                "url": f"https://huggingface.co/{model.get('id')}"
            }
            
            models.append(model_info)
            total_downloads += model_info["downloads"]
            total_likes += model_info["likes"]
        
        # Calculate statistics
        avg_downloads = total_downloads / len(models) if models else 0
        avg_likes = total_likes / len(models) if models else 0
        
        result = {
            "success": True,
            "query": query,
            "task": task,
            "limit": limit,
            "sort": sort,
            "direction": direction,
            "models": models,
            "total_models": len(models),
            "statistics": {
                "total_downloads": total_downloads,
                "total_likes": total_likes,
                "average_downloads": round(avg_downloads, 2),
                "average_likes": round(avg_likes, 2)
            }
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
        return {"error": f"Failed to get Hugging Face models: {str(e)}"}


if __name__ == "__main__":
    # Example usage
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    result = get_huggingface_models_by_task(
        task="text-generation",
        limit=5,
        save_to="./popular_text_generation_models.json"
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))