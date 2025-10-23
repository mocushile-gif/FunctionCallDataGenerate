import requests
import os
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv('NewsAPI_API_KEY', '5702b383a4e24ab5b15e6731f4ec224a')

def search_news_articles(query: str,page: int=1,pageSize: int=10,sortBy:str='publishedAt',from_date: str = None, to_date: str = None, lang: str = None) -> str:
    """
    Search through millions of articles from over 150,000 large and small news sources and blogs using the NewsAPI.

    Parameters:
    - query (str): The search query (e.g., 'apple').
    - page (int): Use this to page through the results.
    - pageSize (int): The number of results to return per page. Default to 10.
    - from_date (str): The date filter for the content, format: 'YYYY-MM-DD'. Optional. up to a month old.
    - to_date (str): The date filter for the content, format: 'YYYY-MM-DD'. Optional.
    - lang (str): The 2-letter ISO-639-1 code of the language you want to get headlines for. Possible options: ar, de,en, es, fr, he, it, nl, no, pt, ru, sv, ud, zh.
    - sortBy (str): The order to sort the articles in. Possible options: relevancy, popularity, publishedAt.
                    relevancy = articles more closely related to q come first.
                    popularity = articles from popular sources and publishers come first.
                    publishedAt = newest articles come first.
                    Default: publishedAt
    """
    url = ('https://newsapi.org/v2/everything?'
       f'q={query}&'
       f'page={page}&'
       f'pageSize={pageSize}&'
       f'sortBy={sortBy}&'
       f'apiKey={api_key}'
       )
    
    if lang:
        url+=f'&language={lang}'
    if from_date:
        url+=f'&from={from_date}'
    if to_date:
        url+=f'&to={to_date}'
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        content_data = response.json()
        return {"response":content_data}
    except Exception as e:
        raise Exception({"error":f"Error fetching News content: {response.text}"})


if __name__ == "__main__":
    # Example usage
    query = "gay"
    
    print(search_news_articles(query,lang='zh'))
