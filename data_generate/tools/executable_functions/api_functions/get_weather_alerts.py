import requests
import os
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv('WeatherAPI_API_KEY', 'd32267b3d3944cc0b1a80559230811')

def get_weather_alerts(q: str)-> str:
    """
    Fetch recent alerts and warnings issued by government agencies (USA, UK, Europe and Rest of the World) as an array if available for the location using the WeatherAPI.
    Fetches weather forecast for a given city using the WeatherAPI.
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

    Returns:
    - str: Weather information or an error message.
    """
    url = f"http://api.weatherapi.com/v1/alerts.json?key={api_key}&q={q}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        alert_data = response.json()
        return {'response':alert_data}
    except Exception as e:
        raise Exception({"error":f"Error fetching weather info: {response.text}"})


if __name__ == "__main__":
    # Example usage
    print(get_weather_alerts("shanghai"))
