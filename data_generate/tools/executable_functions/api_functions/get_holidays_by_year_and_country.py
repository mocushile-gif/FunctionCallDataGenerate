import json
import requests

def get_holidays_by_year_and_country(year: int, country_code: str):
    """
    Retrieves the list of public holidays for a given year and country using the Nager.Date API.

    Parameters:
    - year (int): The year for which to retrieve the holidays.
    - country_code (str): The two-letter ISO 3166-1 alpha-2 country code.

    Returns:
    - list: A list of public holidays in the specified country and year.
    """
    # Construct the URL with the given year and country code
    url = f'https://date.nager.at/api/v3/publicholidays/{year}/{country_code}'
    # Send the request to the API
    try:
        response = requests.get(url)
        if response.status_code==204:
            raise Exception({"error":f"The api does not support this country code: {country_code}, please change."})
        public_holidays = json.loads(response.content)
        # Print the date of each holiday
        string=''
        for public_holiday in public_holidays:
            string+=f"Holiday: {public_holiday['name']} | Date: {public_holiday['date']}\n"
        return string
    except Exception as e:
        raise Exception({"error":f"Error fetching holiday info: {str(e)}"})


# Example usage
if __name__ == "__main__":
    holidays = get_holidays_by_year_and_country(2025, 'US')
    print(holidays)