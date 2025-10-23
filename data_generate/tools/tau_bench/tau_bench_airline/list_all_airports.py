# Copyright Sierra

import json
from typing import Any, Dict

def list_all_airports() -> str:
    airports = [
        "SFO",
        "JFK",
        "LAX",
        "ORD",
        "DFW",
        "DEN",
        "SEA",
        "ATL",
        "MIA",
        "BOS",
        "PHX",
        "IAH",
        "LAS",
        "MCO",
        "EWR",
        "CLT",
        "MSP",
        "DTW",
        "PHL",
        "LGA",
    ]
    cities = [
        "San Francisco",
        "New York",
        "Los Angeles",
        "Chicago",
        "Dallas",
        "Denver",
        "Seattle",
        "Atlanta",
        "Miami",
        "Boston",
        "Phoenix",
        "Houston",
        "Las Vegas",
        "Orlando",
        "Newark",
        "Charlotte",
        "Minneapolis",
        "Detroit",
        "Philadelphia",
        "LaGuardia",
    ]
    return json.dumps({airport: city for airport, city in zip(airports, cities)})

# Example usage:
if __name__ == "__main__":
    print(list_all_airports())