# Copyright Sierra

import json
from copy import deepcopy
from typing import Any, Dict, List
import os
from dotenv import load_dotenv
load_dotenv()

def update_reservation_flights(
    reservation_id: str,
    cabin: str,
    flights: List[Dict[str, Any]],
    payment_id: str) -> str:

    with open('airline.json','r',encoding='utf-8') as f:
        data=json.load(f)

    users, reservations = data["users"], data["reservations"]
    if reservation_id not in reservations:
        return "Error: reservation not found"
    reservation = reservations[reservation_id]

    # update flights and calculate price
    total_price = 0
    flights = deepcopy(flights)
    for flight in flights:
        # if existing flight, ignore
        if _ := [
            f
            for f in reservation["flights"]
            if f["flight_number"] == flight["flight_number"]
            and f["date"] == flight["date"]
            and cabin == reservation["cabin"]
        ]:
            total_price += _[0]["price"] * len(reservation["passengers"])
            flight["price"] = _[0]["price"]
            flight["origin"] = _[0]["origin"]
            flight["destination"] = _[0]["destination"]
            continue
        flight_number = flight["flight_number"]
        if flight_number not in data["flights"]:
            return f"Error: flight {flight_number} not found"
        flight_data = data["flights"][flight_number]
        if flight["date"] not in flight_data["dates"]:
            return (
                f"Error: flight {flight_number} not found on date {flight['date']}"
            )
        flight_date_data = flight_data["dates"][flight["date"]]
        if flight_date_data["status"] != "available":
            return f"Error: flight {flight_number} not available on date {flight['date']}"
        if flight_date_data["available_seats"][cabin] < len(
            reservation["passengers"]
        ):
            return f"Error: not enough seats on flight {flight_number}"
        flight["price"] = flight_date_data["prices"][cabin]
        flight["origin"] = flight_data["origin"]
        flight["destination"] = flight_data["destination"]
        total_price += flight["price"] * len(reservation["passengers"])

    total_price -= sum(flight["price"] for flight in reservation["flights"]) * len(
        reservation["passengers"]
    )

    # check payment
    if payment_id not in users[reservation["user_id"]]["payment_methods"]:
        return "Error: payment method not found"
    payment_method = users[reservation["user_id"]]["payment_methods"][payment_id]
    if payment_method["source"] == "certificate":
        return "Error: certificate cannot be used to update reservation"
    elif (
        payment_method["source"] == "gift_card"
        and payment_method["amount"] < total_price
    ):
        return "Error: gift card balance is not enough"

    # if checks pass, deduct payment and update seats
    if payment_method["source"] == "gift_card":
        payment_method["amount"] -= total_price
    reservation["flights"] = flights
    if total_price != 0:
        reservation["payment_history"].append(
            {
                "payment_id": payment_id,
                "amount": total_price,
            }
        )
    # do not make flight database update here, assume it takes time to be updated
    with open('airline.json','w',encoding='utf-8') as f:
        f.write(json.dumps(data,ensure_ascii=False,indent=4))
    return json.dumps(reservation)

# Example usage:
if __name__ == "__main__":
    os.chdir(os.environ.get("TAU_BENCH_DATA_PATH"))
    arguments={
                    "reservation_id": "FQ8APE",
                    "cabin": "economy",
                    "flights": [
                        {
                            "flight_number": "HAT056",
                            "date": "2024-05-25",
                        },
                        {
                            "flight_number": "HAT138",
                            "date": "2024-05-25",
                        },
                    ],
                    "payment_id": "gift_card_8190333",
                }
    print(update_reservation_flights(**arguments))