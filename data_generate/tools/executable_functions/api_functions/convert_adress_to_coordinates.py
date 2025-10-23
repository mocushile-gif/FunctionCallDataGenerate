import requests
import os
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv('GeoCode_API_KEY', '678908550d581735985977unhcce184')

def convert_adress_to_coordinates(address: str) -> dict:
    """
    Converts an address into geographic coordinates (latitude, longitude).
    
    Parameters:
    - address (str): The address to geocode.

    Returns:
    - dict: A dictionary with latitude and longitude.
    """
    # Construct the URL for the forward geocoding API
    url = f"https://geocode.maps.co/search?q={address}&api_key={api_key}"
    
    # Send the GET request to the API
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    
    # Check if results are found
    if data:
        # Get the first result's coordinates
        lat = data[0].get('lat')
        lon = data[0].get('lon')
        return {'latitude': lat, 'longitude': lon}
    else:
        raise Exception({'error': 'Address not found'})

if __name__ == "__main__":
    # Example usage:
    address = "555 5th Ave, New York, NY 10017, US"
    address = "yizhou"
    coordinates = convert_adress_to_coordinates(address)
    print(coordinates)
