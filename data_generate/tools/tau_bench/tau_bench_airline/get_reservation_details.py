# Copyright Sierra

import json
from typing import Any, Dict
import os
from dotenv import load_dotenv
load_dotenv()

def get_reservation_details(reservation_id: str) -> str:

    with open('airline.json','r',encoding='utf-8') as f:
        data=json.load(f)
    reservations = data["reservations"]
    if reservation_id in reservations:
        return json.dumps(reservations[reservation_id])
    return "Error: user not found"

# Example usage:
if __name__ == "__main__":
    os.chdir(os.environ.get("TAU_BENCH_DATA_PATH"))
    arguments={
              "reservation_id": "Z7GOZK"
            }
    print(get_reservation_details(**arguments))