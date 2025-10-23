import json
from typing import Any, Dict
import os
from dotenv import load_dotenv
load_dotenv()

def modify_user_address(
    user_id: str,
    address1: str,
    address2: str,
    city: str,
    state: str,
    country: str,
    zip: str,
) -> str:

    with open('retail.json','r',encoding='utf-8') as f:
        data=json.load(f)

    users = data["users"]
    if user_id not in users:
        return "Error: user not found"
    user = users[user_id]
    user["address"] = {
        "address1": address1,
        "address2": address2,
        "city": city,
        "state": state,
        "country": country,
        "zip": zip,
    }
    with open('retail.json','w',encoding='utf-8') as f:
        f.write(json.dumps(data,ensure_ascii=False,indent=4))
    return json.dumps(user)

# Example usage:
if __name__ == "__main__":
    os.chdir(os.environ.get("TAU_BENCH_DATA_PATH"))
    arguments={
              "user_id": "ethan_garcia_1261",
              "address1": "101 Highway",
              "address2": "",
              "city": "New York",
              "state": "NY",
              "country": "USA",
              "zip": "10001"
            }
    print(modify_user_address(**arguments))