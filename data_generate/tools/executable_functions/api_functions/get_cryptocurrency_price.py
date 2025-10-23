import os
import json
import requests
from typing import Dict, Any, Optional
from dotenv import load_dotenv
load_dotenv()

def get_cryptocurrency_price(symbol: str = "bitcoin", currency: str = "usd", 
                           include_market_data: bool = False):
    """
    Get current cryptocurrency price and market data.
    
    Parameters:
    - symbol (str): Cryptocurrency symbol (e.g., bitcoin, ethereum, dogecoin)
    - currency (str): Target currency for price (e.g., usd, eur, jpy)
    - include_market_data (bool): Whether to include additional market data
    
    Returns:
    - dict: Cryptocurrency price and market information
    """
    try:
        # Validate parameters
        if not symbol or len(symbol.strip()) == 0:
            return {"error": "Symbol cannot be empty"}
        
        if not currency or len(currency.strip()) == 0:
            return {"error": "Currency cannot be empty"}
        
        # Use CoinGecko API (free, no API key required)
        base_url = "https://api.coingecko.com/api/v3"
        
        # Get basic price data
        price_url = f"{base_url}/simple/price"
        params = {
            "ids": symbol.lower(),
            "vs_currencies": currency.lower(),
            "include_market_cap": include_market_data,
            "include_24hr_vol": include_market_data,
            "include_24hr_change": include_market_data,
            "include_last_updated_at": True
        }
        
        response = requests.get(price_url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if not data or symbol.lower() not in data:
            return {"error": f"Symbol '{symbol}' not found or invalid"}
        
        crypto_data = data[symbol.lower()]
        
        # Get additional market data if requested
        market_data = {}
        if include_market_data:
            try:
                market_url = f"{base_url}/coins/{symbol.lower()}"
                market_response = requests.get(market_url, timeout=10)
                if market_response.status_code == 200:
                    market_info = market_response.json()
                    market_data = {
                        "name": market_info.get("name", symbol),
                        "symbol": market_info.get("symbol", symbol.upper()),
                        "current_price": market_info.get("market_data", {}).get("current_price", {}),
                        "market_cap_rank": market_info.get("market_cap_rank"),
                        "total_volume": market_info.get("market_data", {}).get("total_volume", {}),
                        "high_24h": market_info.get("market_data", {}).get("high_24h", {}),
                        "low_24h": market_info.get("market_data", {}).get("low_24h", {}),
                        "price_change_percentage_24h": market_info.get("market_data", {}).get("price_change_percentage_24h"),
                        "market_cap_change_percentage_24h": market_info.get("market_data", {}).get("market_cap_change_percentage_24h"),
                        "circulating_supply": market_info.get("market_data", {}).get("circulating_supply"),
                        "total_supply": market_info.get("market_data", {}).get("total_supply"),
                        "max_supply": market_info.get("market_data", {}).get("max_supply"),
                        "last_updated": market_info.get("last_updated")
                    }
            except Exception as e:
                print(f"Warning: Could not fetch detailed market data: {e}")
        
        print(crypto_data)
        result = {
            "success": True,
            "symbol": symbol,
            "currency": currency,
            "current_price": crypto_data.get(f"{currency.lower()}", 0),
            "last_updated": crypto_data.get("last_updated_at")
        }
        if include_market_data:
            result.update({"market_cap": crypto_data.get(f"{currency.lower()}_market_cap", 0),
            "volume_24h": crypto_data.get(f"{currency.lower()}_24h_vol", 0),
            "price_change_24h": crypto_data.get(f"{currency.lower()}_24h_change", 0),
            "market_data": market_data if include_market_data else {}})
        
        return result
        
    except requests.exceptions.RequestException as e:
        return {"error": f"Network error: {str(e)}"}
    except Exception as e:
        return {"error": f"Error getting cryptocurrency price: {str(e)}"}



if __name__ == "__main__":
    # Example usage
    result = get_cryptocurrency_price("ethereum", "usd", False)
    print(json.dumps(result, indent=2)) 