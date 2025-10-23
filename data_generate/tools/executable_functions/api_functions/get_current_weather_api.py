import requests
import os
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv('WeatherAPI_API_KEY', 'd32267b3d3944cc0b1a80559230811')

def get_current_weather_api(q: str,include_air_quality:bool=False)-> str:
    """
    Fetches current weather or realtime weather information for a given city using the WeatherAPI.
    Parameters:
    - q (str): Query parameter based on which data is sent back. It could be following:
                Latitude and Longitude (Decimal degree) e.g: q=48.8567,2.3508
                location e.g.: q=Paris (must in English)
                US zip e.g.: q=10001
                UK postcode e.g: q=SW1
                Canada postal code e.g: q=G2J
                metar:<metar code> e.g: q=metar:EGLL
                iata:<3 digit airport code> e.g: q=iata:DXB
                auto:ip IP lookup e.g: q=auto:ip
                IP address (IPv4 and IPv6 supported) e.g: q=100.0.0.1
    - include_air_quality (bool): whether to include air_quality information.

    Returns:
    - str: Weather information or an error message.
    """
    aqi='yes' if include_air_quality else 'no'
    url = f"http://api.weatherapi.com/v1/current.json?key={api_key}&q={q}&aqi={aqi}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        weather_data = response.json()
        return {'response':weather_data}
    except Exception as e:
        raise Exception({"error":f"Error fetching weather info: {response.text}"})

if __name__ == "__main__":
    # Example usage
    # {"function": {"arguments": "{\"q\": \"London\", \"include_air_quality\": true}", "name": "get_current_weather_api"}, "id": "call_6AE8HAWX5Vk5rK1vFUa4YOoS", "type": "function"}
    print(get_current_weather_api("London",True))
