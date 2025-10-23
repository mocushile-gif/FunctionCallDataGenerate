# Copyright Sierra

import json
from typing import Any, Dict
import os
from dotenv import load_dotenv
load_dotenv()

def get_product_details(product_id: str) -> str:

    with open('retail.json','r',encoding='utf-8') as f:
        data=json.load(f)

    products = data["products"]
    if product_id in products:
        return json.dumps(products[product_id])
    return "Error: product not found"

# Example usage:
if __name__ == "__main__":
    os.chdir(os.environ.get("TAU_BENCH_DATA_PATH"))
    print(get_product_details('9523456873'))