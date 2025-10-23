# Copyright Sierra

import json
from typing import Any, Dict
import os
from dotenv import load_dotenv
load_dotenv()

def cancel_reservation(
    reservation_id: str) -> str:

    with open('airline.json','r',encoding='utf-8') as f:
        data=json.load(f)

    reservations = data["reservations"]
    if reservation_id not in reservations:
        return "Error: reservation not found"
    reservation = reservations[reservation_id]

    # reverse the payment
    refunds = []
    for payment in reservation["payment_history"]:
        refunds.append(
            {
                "payment_id": payment["payment_id"],
                "amount": -payment["amount"],
            }
        )
    reservation["payment_history"].extend(refunds)
    reservation["status"] = "cancelled"

    with open('airline.json','w',encoding='utf-8') as f:
        f.write(json.dumps(data,ensure_ascii=False,indent=4))
    return json.dumps(reservation)

# Example usage:
if __name__ == "__main__":
    os.chdir(os.environ.get("TAU_BENCH_DATA_PATH"))
    arguments={
              "reservation_id": "Z7GOZK"
            }
    print(cancel_reservation(**arguments))