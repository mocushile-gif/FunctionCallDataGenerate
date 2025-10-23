# Copyright Sierra

import json
from typing import Any, Dict, List
import os
from dotenv import load_dotenv
load_dotenv()

def update_reservation_passengers(
    reservation_id: str,
    passengers: List[Dict[str, Any]]) -> str:

    with open('airline.json','r',encoding='utf-8') as f:
        data=json.load(f)

    reservations = data["reservations"]
    if reservation_id not in reservations:
        return "Error: reservation not found"
    reservation = reservations[reservation_id]
    if len(passengers) != len(reservation["passengers"]):
        return "Error: number of passengers does not match"
    reservation["passengers"] = passengers

    with open('airline.json','w',encoding='utf-8') as f:
        f.write(json.dumps(data,ensure_ascii=False,indent=4))
    return json.dumps(reservation)

# Example usage:
if __name__ == "__main__":
    os.chdir(os.environ.get("TAU_BENCH_DATA_PATH"))
    arguments={
                    "reservation_id": "FQ8APE",
                    "passengers": [
                        {
                            "first_name": "Omar",
                            "last_name": "Rossi",
                            "dob": "1970-06-06",
                        }
                    ],
                }
    print(update_reservation_passengers(**arguments))
