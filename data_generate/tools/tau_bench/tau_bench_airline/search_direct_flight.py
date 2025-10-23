import json
from typing import Any, Dict
import os
from dotenv import load_dotenv
load_dotenv()

def search_direct_flight(origin: str, destination: str, date: str) -> str:

    with open('airline.json','r',encoding='utf-8') as f:
        data=json.load(f)
    flights = data["flights"]
    results = []
    for flight in flights.values():
        if flight["origin"] == origin and flight["destination"] == destination:
            if (
                date in flight["dates"]
                and flight["dates"][date]["status"] == "available"
            ):
                # results add flight except dates, but add flight["datas"][date]
                results.append({k: v for k, v in flight.items() if k != "dates"})
                results[-1].update(flight["dates"][date])
    return json.dumps(results)


# Example usage:
if __name__ == "__main__":
    os.chdir(os.environ.get("TAU_BENCH_DATA_PATH"))
    arguments={
                    "origin": "BOS",
                    "destination": "MCO",
                    "date": "2024-05-18",
                }
    print(search_direct_flight(**arguments))