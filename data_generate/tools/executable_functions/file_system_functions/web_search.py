import os
import json
import time
import requests
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from duckduckgo_search import DDGS
load_dotenv()


def web_search(
    query: str,
    num_results: int = 5,
    timeout_seconds: int = 20,
    save_path: Optional[str] = None,
    
) -> Dict[str, Any]:

    if not query or not isinstance(query, str) or not query.strip():
        return {
            "status": "failed",
            "error": {
                "error_type": "USER_INPUT_VALIDATION_ERROR",
                "error_code": "INVALID_QUERY",
                "technical_message": "A valid, non-empty search query is required."
            }
        }

    # Try DuckDuckGo first
    try:
        print("🔍 Trying DuckDuckGo search...")
        search_results = []
        with DDGS(timeout=float(timeout_seconds)) as ddgs:
            for i, item in enumerate(ddgs.text(keywords=query, max_results=num_results)):
                if i >= num_results:
                    break
                search_results.append({
                    "title": str(item.get("title", "N/A")),
                    "snippet": str(item.get("body", "N/A")),
                    "link": str(item.get("href", "#"))
                })

        result = {
            "status": "success",
            "data": {
                "engine": "duckduckgo",
                "query": query,
                "num_results_requested": num_results,
                "num_results_returned": len(search_results),
                "results_json_string": json.dumps(search_results, ensure_ascii=False)
            }
        }

    except Exception as e:
        print(f"⚠️ DuckDuckGo failed: {e}\n⏭️ Falling back to Brave...")
        api_key = os.environ.get("BRAVE_API_KEY","BSAdnotPtb1IsFqlIcLAUswod4pu70V")
        if not api_key:
            return {
                "status": "failed",
                "error": {
                    "error_type": "CONFIGURATION_ERROR",
                    "error_code": "MISSING_API_KEY",
                    "technical_message": "BRAVE_API_KEY not set."
                }
            }

        try:
            headers = {
                "Accept": "application/json",
                "X-Subscription-Token": api_key
            }
            params = {
                "q": query,
                "count": num_results
            }
            response = requests.get(
                "https://api.search.brave.com/res/v1/web/search",
                headers=headers,
                params=params,
                timeout=timeout_seconds
            )
            response.raise_for_status()

            raw_results = response.json().get("web", {}).get("results", [])
            search_results = [{
                "title": r.get("title", "N/A"),
                "snippet": r.get("description", "N/A"),
                "link": r.get("url", "#")
            } for r in raw_results]

            result = {
                "status": "success",
                "data": {
                    "engine": "brave",
                    "query": query,
                    "num_results_requested": num_results,
                    "num_results_returned": len(search_results),
                    "results_json_string": json.dumps(search_results, ensure_ascii=False)
                }
            }

        except Exception as be:
            return {
                "status": "failed",
                "error": {
                    "error_type": "HTTP_REQUEST_ERROR",
                    "error_code": "FALLBACK_FAILED",
                    "technical_message": f"Web Search Failed: {be}"
                }
            }

    # 保存结果
    if save_path:
        try:
            os.makedirs(os.path.dirname(save_path) or '.', exist_ok=True)
            with open(save_path, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            result.setdefault("data", {})["saved_to"] = save_path
        except Exception as se:
            result["status"] = "partial_success"
            result["warning"] = f"Search succeeded, but failed to save to file: {se}"

    return result

if __name__ == "__main__":
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    response = web_search(
        "recent updates on United States economy", 
        num_results=5,
        save_path="./search_results.json"
        )
    print(json.dumps(response, indent=2, ensure_ascii=False))
