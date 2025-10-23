import requests
from typing import Union, List
import os
from dotenv import load_dotenv
load_dotenv()

def get_current_exchange_rate(base_currency: str, target_currency: Union[str, List[str]]) -> dict:
    """
    Fetches the exchange rates between a base currency and one or more target currencies using the API Layer.

    Parameters:
    - base_currency (str): The base currency code (e.g., 'USD' for US Dollar, 'EUR' for Euro).
    - target_currency (Union[str, List[str]]): The target currency code or a list of target currency codes 
                                                (e.g., 'EUR', 'GBP', ['EUR', 'GBP', 'CAD']).

    Returns:
    - dict: The exchange rate data in JSON format.
            If the request is successful, the data contains the exchange rates for the specified target currencies.
            In case of an error, an error message is returned.
    """
    api_key = os.getenv('APILayer_API_KEY', 'a428a2e1c061d2c5c5b24c784e87f5b9')
    # Check if target_currency is a list and join it into a comma-separated string
    if isinstance(target_currency, list):
        target_currency = ','.join(target_currency)
    
    # Construct the API URL with the provided parameters
    url = f'http://apilayer.net/api/live?access_key={api_key}&source={base_currency}&currencies={target_currency}&format=1'
    # Make the API request
    response = requests.get(url)
    
    # Raise exception for unsuccessful requests
    response.raise_for_status()
    
    # Check if the response contains 'quotes' field and return it
    data = response.json()
    return {'response':data}
    
# Example usage
if __name__ == "__main__":
    exchange_rate = get_current_exchange_rate("USD", ["EUR", "GBP", "CAD", "PLN"])
    print(exchange_rate)
