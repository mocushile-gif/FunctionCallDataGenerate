import requests
import os
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv('GeoCode_API_KEY', '678908550d581735985977unhcce184')

def convert_coordinates_to_adress(latitude: float, longitude: float) -> dict:
    """
    Converts geographic coordinates (latitude, longitude) into an address.
    
    Parameters:
    - latitude (float): The latitude to reverse geocode.
    - longitude (float): The longitude to reverse geocode.

    Returns:
    - dict: A dictionary with the address details.
    """
    # Construct the URL for the reverse geocoding API
    url = f"https://geocode.maps.co/reverse?lat={latitude}&lon={longitude}&api_key={api_key}"
    
    # Send the GET request to the API
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    # Check if result is found
    if data:
        return data  # Return the address details from the first result
    else:
        raise Exception({'error': 'Coordinates not found'})

if __name__ == "__main__":
    # Example usage:
    latitude = 24
    longitude = 108
    address = convert_coordinates_to_adress(latitude, longitude)
    print(address)
