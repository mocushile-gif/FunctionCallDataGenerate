import requests
import os
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv('APILayer_API_KEY', 'a428a2e1c061d2c5c5b24c784e87f5b9')

def convert_currency_api(from_currency: str, to_currency: str, amount: float) -> dict:
    """
    Converts an amount from one currency to another using the CurrencyLayer API.

    Parameters:
    - from_currency (str): The base currency code (e.g., 'USD', 'EUR').
    - to_currency (str): The target currency code (e.g., 'GBP', 'CAD').
    - amount (float): The amount of money to convert.

    Returns:
    - dict: A dictionary containing the conversion result, including the converted amount and exchange rate.
            If the request is successful, it returns the converted amount.
            If an error occurs, it returns an error message.
    """
    url = f'https://api.currencylayer.com/convert?access_key={api_key}&'
    params = {
        'from': from_currency,
        'to': to_currency,
        'amount': amount
    }

    # Make the API request
    response = requests.get(url, params=params)
    response.raise_for_status()  # Check if the request was successful
    
    # Return the JSON response from the API
    data = response.json()
    return {"response":data}

# Example usage
if __name__ == "__main__":
    result = convert_currency_api("GBP", "CAD", 200)
    print(result)
