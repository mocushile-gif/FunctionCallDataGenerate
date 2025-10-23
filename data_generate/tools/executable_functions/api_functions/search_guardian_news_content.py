import requests
import os
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv('Guardian_API_KEY', 'a6c3de51-f970-4626-96f0-6008257e8e51')

def search_guardian_news_content(query: str, page: int = 1, from_date: str = None, tag: str = None) -> str:
    """
    Search news content from The Guardian using the Guardian API based on a search query and additional filters.

    Parameters:
    - query (str): The search query (e.g., 'debate').
    - page (int): The page number for paginated results. Default is 1.
    - from_date (str): The date filter for the content, format: 'YYYY-MM-DD'. Optional.
    - tag (str): A specific tag to filter the results (e.g., 'politics/politics'). Optional.

    Returns:
    - str: JSON response or an error message.
    """
    url = f"https://content.guardianapis.com/search?q={query}&api-key={api_key}&page={page}"

    # Add date filter if provided
    if from_date:
        url += f"&from-date={from_date}"

    # Add tag filter if provided
    if tag:
        url += f"&tag={tag}"

    try:
        response = requests.get(url)
        response.raise_for_status()
        content_data = response.json()
        return {"response":content_data}
    except Exception as e:
        raise Exception({"error":f"Error fetching Guardian content: {response.text}"})


if __name__ == "__main__":
    # Example usage
    query = "gay"
    page = 1
    from_date = "2024-01-01"
    tag = "politics/politics"
    
    print(search_guardian_news_content(query, page, from_date, tag))
