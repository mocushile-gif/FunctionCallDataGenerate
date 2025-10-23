import json
from typing import Any, Dict
import os
from dotenv import load_dotenv
load_dotenv()

def modify_pending_order_address(
    order_id: str,
    address1: str,
    address2: str,
    city: str,
    state: str,
    country: str,
    zip: str
) -> str:

    with open('retail.json','r',encoding='utf-8') as f:
        data=json.load(f)
    # Check if the order exists and is pending
    orders = data["orders"]
    if order_id not in orders:
        return "Error: order not found"
    order = orders[order_id]
    if order["status"] != "pending":
        return "Error: non-pending order cannot be modified"

    # Modify the address
    order["address"] = {
        "address1": address1,
        "address2": address2,
        "city": city,
        "state": state,
        "country": country,
        "zip": zip,
    }
    with open('retail.json','w',encoding='utf-8') as f:
        f.write(json.dumps(data,ensure_ascii=False,indent=4))
    return json.dumps(order)

# Example usage:
if __name__ == "__main__":
    os.chdir(os.environ.get("TAU_BENCH_DATA_PATH"))
    arguments={
                    "order_id": "#W8665881",
                    "address1": "123 Elm Street",
                    "address2": "Suite 641",
                    "city": "Austin",
                    "state": "TX",
                    "country": "USA",
                    "zip": "78712",
                }
    print(modify_pending_order_address(**arguments))
