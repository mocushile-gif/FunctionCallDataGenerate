# Copyright Sierra

import json
from typing import Any, Dict
import os
from dotenv import load_dotenv
load_dotenv()

def cancel_pending_order(order_id: str, reason: str) -> str:

    with open('retail.json','r',encoding='utf-8') as f:
        data=json.load(f)
    # check order exists and is pending
    orders = data["orders"]
    if order_id not in orders:
        return "Error: order not found"
    order = orders[order_id]
    if order["status"] != "pending":
        return "Error: non-pending order cannot be cancelled"

    # check reason
    if reason not in ["no longer needed", "ordered by mistake"]:
        return "Error: invalid reason"

    # handle refund
    refunds = []
    for payment in order["payment_history"]:
        payment_id = payment["payment_method_id"]
        refund = {
            "transaction_type": "refund",
            "amount": payment["amount"],
            "payment_method_id": payment_id,
        }
        refunds.append(refund)
        if "gift_card" in payment_id:  # refund to gift card immediately
            payment_method = data["users"][order["user_id"]]["payment_methods"][
                payment_id
            ]
            payment_method["balance"] += payment["amount"]
            payment_method["balance"] = round(payment_method["balance"], 2)

    # update order status
    order["status"] = "cancelled"
    order["cancel_reason"] = reason
    order["payment_history"].extend(refunds)

    with open('retail.json','w',encoding='utf-8') as f:
        f.write(json.dumps(data,ensure_ascii=False,indent=4))
    return json.dumps(order)

# Example usage:
if __name__ == "__main__":
    os.chdir(os.environ.get("TAU_BENCH_DATA_PATH"))
    arguments={
                "order_id": "#W5199551",
                "reason": "no longer needed"
                }
    print(cancel_pending_order(**arguments))