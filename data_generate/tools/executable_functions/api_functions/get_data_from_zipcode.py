import requests

def get_data_from_zipcode(zipcode: str) -> str:
    """
    Retrieves the data for a given ZIP code using the Ziptastic API.

    Parameters:
    - zipcode (str): The ZIP code to look up.

    Returns:
    - str: The name of the city corresponding to the ZIP code.
    """
    # Construct the URL to call the Ziptastic API
    url = f"http://ZiptasticAPI.com/{zipcode}"
    
    # Make the API request
    response = requests.get(url)
    response.raise_for_status() 
    data = response.json()
    return data

# Example usage
if __name__ == "__main__":
    zipcode = "90210"  # Example ZIP code
    data = get_data_from_zipcode(zipcode)
    print(data)
