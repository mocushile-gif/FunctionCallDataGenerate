import json
from typing import Any, Dict, List
import os
from dotenv import load_dotenv
load_dotenv()

def return_delivered_order_items(
    order_id: str, item_ids: List[str], payment_method_id: str, 
) -> str:

    with open('retail.json','r',encoding='utf-8') as f:
        data=json.load(f)

    orders = data["orders"]

    # Check if the order exists and is delivered
    if order_id not in orders:
        return "Error: order not found"
    order = orders[order_id]
    if order["status"] != "delivered":
        return "Error: non-delivered order cannot be returned"

    # Check if the payment method exists and is either the original payment method or a gift card
    if payment_method_id not in data["users"][order["user_id"]]["payment_methods"]:
        return "Error: payment method not found"
    if (
        "gift_card" not in payment_method_id
        and payment_method_id != order["payment_history"][0]["payment_method_id"]
    ):
        return "Error: payment method should be either the original payment method or a gift card"

    # Check if the items to be returned exist (there could be duplicate items in either list)
    all_item_ids = [item["item_id"] for item in order["items"]]
    for item_id in item_ids:
        if item_ids.count(item_id) > all_item_ids.count(item_id):
            return "Error: some item not found"

    # Update the order status
    order["status"] = "return requested"
    order["return_items"] = sorted(item_ids)
    order["return_payment_method_id"] = payment_method_id

    with open('retail.json','w',encoding='utf-8') as f:
        f.write(json.dumps(data,ensure_ascii=False,indent=4))
    return json.dumps(order)

# Example usage:
if __name__ == "__main__":
    os.chdir(os.environ.get("TAU_BENCH_DATA_PATH"))
    arguments={
              "order_id": "#W2890441",
              "item_ids": [
                "2366567022"
              ],
              "payment_method_id": "credit_card_1061405"
            }
    print(return_delivered_order_items(**arguments))