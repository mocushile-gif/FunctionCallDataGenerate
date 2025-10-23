import requests

def get_ip_info(query=None, fields=None, lang=None):
    """
    Get IP or domain information from ip-api.com API.

    :param query: The IP address or domain name to query. If None, the current IP is used.
    :param fields: The fields to include in the response. Can be a comma-separated string. Example: 'status,message,country,countryCode,region,regionName,city,zip,lat,lon,timezone,isp,org,as,query' (optional)
    :param lang: The response language (must be one of the supported languages). Supported languages: 'en', 'de', 'es', 'pt-BR', 'fr', 'ja', 'zh-CN', 'ru'. Default to 'en'.
    """
    # Validate language
    supported_languages = {"en", "de", "es", "pt-BR", "fr", "ja", "zh-CN", "ru"}
    if lang not in supported_languages:
        print(f"Invalid language '{lang}', defaulting to English ('en').")
        lang = "en"
    
    # Validate fields
    valid_fields = {
        "status", "message", "query", "continent", "continentCode", "country", "countryCode", "region",
        "regionName", "city", "district", "zip", "lat", "lon", "timezone", "offset", "currency",
        "isp", "org", "as", "asname", "reverse", "mobile", "proxy", "hosting"
    }
    if fields:
        # Convert fields to a set for validation if it's a string
        if isinstance(fields, str):
            field_list = fields.split(",")
            invalid_fields = [field for field in field_list if field not in valid_fields]
            if invalid_fields:
                raise ValueError(f"Invalid fields specified: {', '.join(invalid_fields)}. Valid fields: ['status', 'message', 'query', 'continent', 'continentCode', 'country', 'countryCode', 'region', 'regionName', 'city', 'district', 'zip', 'lat', 'lon', 'timezone', 'offset', 'currency', 'isp', 'org', 'as', 'asname','reverse', 'mobile', 'proxy', 'hosting']")
        elif not isinstance(fields, int):
            raise ValueError("Fields must be a comma-separated string.")
    
    base_url = "http://ip-api.com/json/"
    url = f"{base_url}{query or ''}"
    
    params = {}
    if fields:
        params['fields'] = fields
    if lang:
        params['lang'] = lang
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        # JSONP responses wrap the JSON in a callback, so return the raw text if callback is used
        return response.json()
    except Exception as e:
        raise Exception({"error":response.text})


# Example usage
if __name__ == "__main__":
    query_result = get_ip_info(lang="en",fields='')
    print(query_result)
