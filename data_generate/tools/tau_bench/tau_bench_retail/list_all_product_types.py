import json
from typing import Any, Dict
import os
from dotenv import load_dotenv
load_dotenv()

def list_all_product_types() -> str:

    with open('retail.json','r',encoding='utf-8') as f:
        data=json.load(f)

    products = data["products"]
    product_dict = {
        product["name"]: product["product_id"] for product in products.values()
    }
    product_dict = dict(sorted(product_dict.items()))
    return json.dumps(product_dict)

# Example usage:
if __name__ == "__main__":
    os.chdir(os.environ.get("TAU_BENCH_DATA_PATH"))
    print(list_all_product_types())