import requests
import os
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv('WeatherAPI_API_KEY', 'd32267b3d3944cc0b1a80559230811')

def get_weather_history(q: str,dt:str=None,end_dt:str=None,include_astro:bool=False,include_hour_forecast:bool=False)-> str:
    """
    Fetches weather forecast for a given city using the WeatherAPI. The API is limited to retrieving historical data for up to 7 days in the past.
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
    - dt (str): should be on or after 1st Jan, 2010 in yyyy-MM-dd format (i.e. dt=2010-01-01).
    - end_dt (str): should be on or after 1st Jan, 2010 in yyyy-MM-dd format (i.e. dt=2010-01-01). 'end_dt' should be greater than 'dt' parameter and difference should not be more than 30 days between the two dates.
    - include_astro (bool): whether to include astro element contains sunrise, sunset, moonrise, moonphase and moonset data. Default to False.
    - include_hour_forecast (bool): whether to include hour by hour weather forecast information. Default to False.
    
    Returns:
    - str: Weather information or an error message.
    """
    if not dt and not end_dt:
        return {'error':'either dt or end_dt parameter should be provided.'}
    url = f"http://api.weatherapi.com/v1/history.json?key={api_key}&q={q}&dt={dt}&end_dt={end_dt}"
        
    try:
        response = requests.get(url)
        response.raise_for_status()
        weather_data = response.json()
        if 'error' in weather_data and weather_data['error']:
            return weather_data
        for day in weather_data['forecast']['forecastday']:
            if not include_astro:
                del day['astro']
            if not include_hour_forecast:
                del day['hour']
        # forecast_by_day=[{'date':day['date'],'day':day['day']} for day in weather_data['forecast']['forecastday']]
        return {"response":{"location":weather_data['location'],'forecast':weather_data['forecast']['forecastday']}}
    except Exception as e:
        raise Exception({"error":f"Error fetching weather info: {response.text}"})

if __name__ == "__main__":
    # Example usage
    print(get_weather_history("London",dt="2025-08-01"))
