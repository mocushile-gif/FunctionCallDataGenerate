# Copyright Sierra

import json
from typing import Any, Dict
import os
from dotenv import load_dotenv
load_dotenv()

def get_order_details(order_id: str):
    with open('retail.json','r',encoding='utf-8') as f:
        data=json.load(f)

    orders = data["orders"]
    if order_id in orders:
        return json.dumps(orders[order_id])
    return "Error: order not found"

# Example usage:
if __name__ == "__main__":
    os.chdir(os.environ.get("TAU_BENCH_DATA_PATH"))
    print(get_order_details('#W2611340'))
    
