import json
from copy import deepcopy
from typing import Any, Dict, List
import os
from dotenv import load_dotenv
load_dotenv()

def book_reservation(
    user_id: str,
    origin: str,
    destination: str,
    flight_type: str,
    cabin: str,
    flights: List[Dict[str, Any]],
    passengers: List[Dict[str, Any]],
    payment_methods: List[Dict[str, Any]],
    total_baggages: int,
    nonfree_baggages: int,
    insurance: str) -> str:

    with open('airline.json','r',encoding='utf-8') as f:
        data=json.load(f)

    reservations, users = data["reservations"], data["users"]
    if user_id not in users:
        return "Error: user not found"
    user = users[user_id]

    reservation_id = "HATHAT"
    if reservation_id in reservations:
        reservation_id = "HATHAU"
        if reservation_id in reservations:
            reservation_id = "HATHAV"

    reservation = {
        "reservation_id": reservation_id,
        "user_id": user_id,
        "origin": origin,
        "destination": destination,
        "flight_type": flight_type,
        "cabin": cabin,
        "flights": deepcopy(flights),
        "passengers": passengers,
        "payment_history": payment_methods,
        "created_at": "2024-05-15T15:00:00",
        "total_baggages": total_baggages,
        "nonfree_baggages": nonfree_baggages,
        "insurance": insurance,
    }

    total_price = 0
    for flight in reservation["flights"]:
        flight_number = flight["flight_number"]
        if flight_number not in data["flights"]:
            return f"Error: flight {flight_number} not found"
        flight_data = data["flights"][flight_number]
        if flight["date"] not in flight_data["dates"]:
            return f"Error: flight {flight_number} not found on date {flight['date']}"
        flight_date_data = flight_data["dates"][flight["date"]]
        if flight_date_data["status"] != "available":
            return f"Error: flight {flight_number} not available on date {flight['date']}"
        if flight_date_data["available_seats"][cabin] < len(passengers):
            return f"Error: not enough seats on flight {flight_number}"
        flight["price"] = flight_date_data["prices"][cabin]
        flight["origin"] = flight_data["origin"]
        flight["destination"] = flight_data["destination"]
        total_price += flight["price"] * len(passengers)

    if insurance == "yes":
        total_price += 30 * len(passengers)
    total_price += 50 * nonfree_baggages

    for payment_method in payment_methods:
        payment_id = payment_method["payment_id"]
        amount = payment_method["amount"]
        if payment_id not in user["payment_methods"]:
            return f"Error: payment method {payment_id} not found"
        if user["payment_methods"][payment_id]["source"] in ["gift_card", "certificate"]:
            if user["payment_methods"][payment_id]["amount"] < amount:
                return f"Error: not enough balance in payment method {payment_id}"
    if sum(payment["amount"] for payment in payment_methods) != total_price:
        return f"Error: payment amount does not add up, total price is {total_price}, but paid {sum(payment['amount'] for payment in payment_methods)}"

    for payment_method in payment_methods:
        payment_id = payment_method["payment_id"]
        amount = payment_method["amount"]
        if user["payment_methods"][payment_id]["source"] == "gift_card":
            user["payment_methods"][payment_id]["amount"] -= amount
        elif user["payment_methods"][payment_id]["source"] == "certificate":
            del user["payment_methods"][payment_id]

    reservations[reservation_id] = reservation
    user["reservations"].append(reservation_id)

    with open('airline.json','w',encoding='utf-8') as f:
        f.write(json.dumps(data,ensure_ascii=False,indent=4))
    return json.dumps(reservation)

# Example usage:
if __name__ == "__main__":
    os.chdir(os.environ.get("TAU_BENCH_DATA_PATH"))
    arguments={
                    "user_id": "mohamed_silva_9265",
                    "origin": "JFK",
                    "destination": "SFO",
                    "flight_type": "round_trip",
                    "cabin": "business",
                    "flights": [
                        {"flight_number": "HAT023", "date": "2024-05-26"},
                        {"flight_number": "HAT204", "date": "2024-05-28"},
                        {"flight_number": "HAT100", "date": "2024-05-28"},
                    ],
                    "passengers": [
                        {
                            "first_name": "Mohamed",
                            "last_name": "Silva",
                            "dob": "1960-11-26",
                        },
                        {
                            "first_name": "Raj",
                            "last_name": "Sanchez",
                            "dob": "1986-09-12",
                        },
                        {
                            "first_name": "Liam",
                            "last_name": "Wilson",
                            "dob": "1980-03-27",
                        },
                    ],
                    "payment_methods": [
                        {"payment_id": "certificate_3765853", "amount": 500},
                        {"payment_id": "gift_card_8020792", "amount": 198},
                        {"payment_id": "gift_card_6136092", "amount": 129},
                        {"payment_id": "credit_card_2198526", "amount": 1786},
                    ],
                    "total_baggages": 0,
                    "nonfree_baggages": 0,
                    "insurance": "no",
                }
    print(book_reservation(**arguments))