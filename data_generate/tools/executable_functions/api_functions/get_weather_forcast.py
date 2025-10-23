import requests
import os
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv('WeatherAPI_API_KEY', 'd32267b3d3944cc0b1a80559230811')

def get_weather_forcast(q: str,dt:str=None,days:int=1,include_astro:bool=False,include_hour_forecast:bool=False)-> str:
    """
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
    - dt (str): Restrict date output. dt' should be between today and next 3 day in yyyy-MM-dd format (i.e. dt=2025-01-01)
    - days (int): Number of days of forecast required, ranging between 1 and 3. Default to 1.
    - include_astro (bool): whether to include astro element contains sunrise, sunset, moonrise, moonphase and moonset data. Default to False.
    - include_hour_forecast (bool): whether to include hour by hour weather forecast information. Default to False.
    
    Returns:
    - str: Weather information or an error message.
    """
    url = f"http://api.weatherapi.com/v1/forecast.json?key={api_key}&q={q}&dt={dt}&days={days}"
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
        return {"response":{'location':weather_data['location'],'forecast':weather_data['forecast']['forecastday']}}
    except Exception as e:
        raise Exception({"error":f"Error fetching weather info: {response.text}"})


if __name__ == "__main__":
    # Example usage
    print(get_weather_forcast("yizhou,hechi,guangxi",days=1,include_hour_forecast=True))
