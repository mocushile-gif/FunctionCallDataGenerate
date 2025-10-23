import requests
import os
from dotenv import load_dotenv
load_dotenv()

def get_stock_data(symbol: str, time_unit: str='day', limit: int=100, interval: str='5min') -> str:
    """
    Fetches the stock data for a given symbol using the Alpha Vantage API.

    Parameters:
    - symbol (str): The stock ticker symbol (e.g., 'AAPL' for Apple, 'GOOG' for Google).
    - time_unit (str): The time unit for the stock data. Possible values are:
      - 'day' (default): Daily stock data.
      - 'week': Weekly stock data.
      - 'month': Monthly stock data.
      - 'intraday': Intraday stock data (requires the 'interval' parameter).
    - limit (int): Returns only the latest 'limit' data points (e.g., 100). Default is 100.
    - interval (str): Only applicable when `time_unit` is 'intraday'. Defines the time interval between two consecutive data points in the time series. Supported values are:
      - '1min', '5min', '15min', '30min', '60min'.

    Returns:
    - dict: Stock data in JSON format or an error message if the request fails.
    """
    api_key = os.getenv('AlphaVantage_API_KEY', "KTRKSANGNM0IEOKG")
    # Validate symbol (must be a non-empty string)
    if not isinstance(symbol, str) or not symbol.strip():
        return "Error: The 'symbol' must be a non-empty string."
    
    # Validate time_unit
    valid_time_units = ['day', 'week', 'month', 'intraday']
    if time_unit not in valid_time_units:
        return f"Error: Invalid 'time_unit' specified. Use one of {valid_time_units}."

    # Validate limit (must be a positive integer)
    if not isinstance(limit, int) or limit <= 0:
        return "Error: The 'limit' parameter must be a positive integer."

    # Validate interval (only for 'intraday' time_unit)
    if time_unit == 'intraday' and interval not in ['1min', '5min', '15min', '30min', '60min']:
        return "Error: Invalid 'interval' specified. Use one of ['1min', '5min', '15min', '30min', '60min']."

    url = f"https://www.alphavantage.co/query"
    if time_unit=='day':
        function="TIME_SERIES_DAILY"
    elif time_unit=='week':
        function="TIME_SERIES_WEEKLY"
    elif time_unit=='month':
        function="TIME_SERIES_MONTHLY"
    elif time_unit=='intraday':
        function="TIME_SERIES_INTRADAY"

    params = {
        "function": function,  # Daily stock prices
        "symbol": symbol,                 # Stock symbol
        "apikey": "KTRKSANGNM0IEOKG",                # Your API key
        "outputsize": "compact"
    }
    if time_unit=='intraday':
        params['interval']=interval

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Check if the request was successful
        stock_data = response.json()
        stock_data[list(stock_data.keys())[1]]=dict(list(stock_data[list(stock_data.keys())[1]].items())[:limit])
        
        # Check if the data contains 'Time Series (Daily)' key
        return {'response':stock_data}
    except Exception as e:
        raise Exception({"error":f"Error fetching stock data: {response.text}"})


if __name__ == "__main__":
    # Example usage
    
    symbol = "AAPL"  # Stock ticker symbol, e.g., 'AAPL' for Apple
    stock_data = get_stock_data(symbol,'intraday',limit=10,interval='15min')
    print(stock_data)
