import os
import json
import time
import requests
from typing import Dict, Any, Optional
from duckduckgo_search import DDGS
from dotenv import load_dotenv
load_dotenv()

def duckduckgo_websearch(
    query: str,
    num_results: int = 5,
    timeout_seconds: int = 20,
) -> Dict[str, Any]:
    api_key = os.environ.get("BRAVE_API_KEY","BSAdnotPtb1IsFqlIcLAUswod4pu70V")
    if not query or not isinstance(query, str) or not query.strip():
        raise Exception({
            "status": "failed",
            "error": {
                "error_type": "USER_INPUT_VALIDATION_ERROR",
                "error_code": "INVALID_QUERY",
                "technical_message": "A valid, non-empty search query is required."
            }
        })

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
        if not api_key:
            raise Exception({
                "status": "failed",
                "error": {
                    "error_type": "CONFIGURATION_ERROR",
                    "error_code": "MISSING_API_KEY",
                    "technical_message": "BRAVE_API_KEY not set."
                }
            })

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
            raise Exception({
                "status": "failed",
                "error": {
                    "error_type": "HTTP_REQUEST_ERROR",
                    "error_code": "FALLBACK_FAILED",
                    "technical_message": f"Web Search Failed: {be}"
                }
            })

    return result

if __name__ == "__main__":
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    response = duckduckgo_websearch(
        "Why Mann–Whitney U test results might not be statistically significant even with large sample sizes", 
        num_results=5,)
    print(json.dumps(response, indent=2, ensure_ascii=False))
