import os
import json
import requests
from typing import Dict, Any, Optional
from dotenv import load_dotenv
load_dotenv()

def get_country_info(name: str = "Japan", include_details: bool = True, 
                    output_path: Optional[str] = None):
    """
    Get comprehensive country information from restcountries API.
    
    Parameters:
    - name (str): Country name (e.g., "China", "Brazil", "Japan")
    - include_details (bool): Whether to include detailed information
    - output_path (str, optional): Path to save country information
    
    Returns:
    - dict: Country information including capital, population, currencies, etc.
    """
    try:
        # Validate parameters
        if not name or len(name.strip()) == 0:
            return {"error": "Country name cannot be empty"}
        
        # Use restcountries API
        url = f"https://restcountries.com/v3.1/name/{name}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if not data:
            return {"error": f"Country '{name}' not found"}
        
        country_data = data[0]
        
        # Extract key information
        basic_info = {
            "name": {
                "common": country_data.get("name", {}).get("common", name),
                "official": country_data.get("name", {}).get("official", ""),
                "native_names": country_data.get("name", {}).get("nativeName", {})
            },
            "capital": country_data.get("capital", []),
            "region": country_data.get("region", ""),
            "subregion": country_data.get("subregion", ""),
            "population": country_data.get("population", 0),
            "area": country_data.get("area", 0),
            "currencies": country_data.get("currencies", {}),
            "languages": country_data.get("languages", {}),
            "flag": country_data.get("flag", ""),
            "flag_emoji": country_data.get("flag", ""),
            "timezones": country_data.get("timezones", []),
            "continents": country_data.get("continents", []),
            "borders": country_data.get("borders", []),
            "independent": country_data.get("independent", False),
            "un_member": country_data.get("unMember", False),
            "landlocked": country_data.get("landlocked", False),
            "fifa": country_data.get("fifa", ""),
            "car": {
                "side": country_data.get("car", {}).get("side", ""),
                "signs": country_data.get("car", {}).get("signs", [])
            },
            "postal_code": country_data.get("postalCode", {}),
            "coat_of_arms": country_data.get("coatOfArms", {}),
            "maps": country_data.get("maps", {}),
            "idd": country_data.get("idd", {}),
            "gini": country_data.get("gini", {}),
            "demonyms": country_data.get("demonyms", {}),
            "tld": country_data.get("tld", []),
            "cca2": country_data.get("cca2", ""),
            "cca3": country_data.get("cca3", ""),
            "ccn3": country_data.get("ccn3", ""),
            "cioc": country_data.get("cioc", ""),
            "status": country_data.get("status", ""),
            "capital_info": country_data.get("capitalInfo", {}),
            "start_of_week": country_data.get("startOfWeek", ""),
            "latlng": country_data.get("latlng", []),
            "translations": country_data.get("translations", {})
        }
        
        # Calculate additional metrics
        population_formatted = f"{basic_info['population']:,}" if basic_info['population'] else "Unknown"
        area_formatted = f"{basic_info['area']:,} km²" if basic_info['area'] else "Unknown"
        
        # Currency information
        currencies_info = []
        for code, currency in basic_info['currencies'].items():
            currencies_info.append({
                "code": code,
                "name": currency.get("name", ""),
                "symbol": currency.get("symbol", "")
            })
        
        # Language information
        languages_info = []
        for code, language in basic_info['languages'].items():
            languages_info.append({
                "code": code,
                "name": language
            })
        
        # Geographic information
        geographic_info = {
            "coordinates": basic_info['latlng'],
            "borders_count": len(basic_info['borders']),
            "borders": basic_info['borders'],
            "landlocked": basic_info['landlocked'],
            "continents": basic_info['continents']
        }
        
        # Economic and social indicators
        economic_info = {
            "population": {
                "total": basic_info['population'],
                "formatted": population_formatted
            },
            "area": {
                "total_km2": basic_info['area'],
                "formatted": area_formatted
            },
            "currencies": currencies_info,
            "gini_coefficient": basic_info['gini'],
            "languages": languages_info
        }
        
        # Political and administrative info
        political_info = {
            "capital": basic_info['capital'],
            "region": basic_info['region'],
            "subregion": basic_info['subregion'],
            "independent": basic_info['independent'],
            "un_member": basic_info['un_member'],
            "fifa_member": bool(basic_info['fifa']),
            "fifa_code": basic_info['fifa'],
            "status": basic_info['status']
        }
        
        # Contact and identification
        contact_info = {
            "country_codes": {
                "cca2": basic_info['cca2'],
                "cca3": basic_info['cca3'],
                "ccn3": basic_info['ccn3'],
                "cioc": basic_info['cioc']
            },
            "top_level_domain": basic_info['tld'],
            "international_dialing": basic_info['idd'],
            "postal_code_format": basic_info['postal_code'].get("format", ""),
            "postal_code_regex": basic_info['postal_code'].get("regex", "")
        }
        
        result = {
            "country_name": {
                "common": basic_info['name']['common'],
                "official": basic_info['name']['official']
            },
            "geographic_info": geographic_info,
            "economic_info": economic_info,
            "political_info": political_info,
            "contact_info": contact_info,
            "cultural_info": {
                "languages": languages_info,
                "currencies": currencies_info,
                "timezones": basic_info['timezones'],
                "start_of_week": basic_info['start_of_week'],
                "demonyms": basic_info['demonyms']
            },
            "symbols": {
                "flag": basic_info['flag'],
                "flag_emoji": basic_info['flag_emoji'],
                "coat_of_arms": basic_info['coat_of_arms']
            },
            "maps": basic_info['maps'],
            "translations": basic_info['translations'],
            "operation": "get_country_info",
            "parameters": {
                "name": name,
                "include_details": include_details
            },
            "success": True
        }
        
        # Save to file if output_path is provided
        if output_path:
            try:
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(result, f, indent=2, ensure_ascii=False)
                result["output_path"] = output_path
            except Exception as e:
                print(f"Warning: Could not save to file: {e}")
        
        return result
        
    except requests.exceptions.RequestException as e:
        return {"error": f"Network error: {str(e)}"}
    except Exception as e:
        return {"error": f"Error getting country info: {str(e)}"}


if __name__ == "__main__":
    # Example usage
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    result = get_country_info("Japan")
    print(json.dumps(result, indent=2, ensure_ascii=False)) 