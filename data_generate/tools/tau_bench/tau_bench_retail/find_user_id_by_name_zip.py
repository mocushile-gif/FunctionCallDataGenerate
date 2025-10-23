from typing import Any, Dict
import json
import os
from dotenv import load_dotenv
load_dotenv()

def find_user_id_by_name_zip(first_name: str, last_name: str, zip: str) -> str:

    with open('retail.json','r',encoding='utf-8') as f:
        data=json.load(f)

    users = data["users"]
    for user_id, profile in users.items():
        if (
            profile["name"]["first_name"].lower() == first_name.lower()
            and profile["name"]["last_name"].lower() == last_name.lower()
            and profile["address"]["zip"] == zip
        ):
            return user_id
    return "Error: user not found"

# Example usage:
if __name__ == "__main__":
    os.chdir(os.environ.get("TAU_BENCH_DATA_PATH"))
    arguments={'first_name': 'Fatima', 'last_name': 'Johnson', 'zip': '78712'}
    print(find_user_id_by_name_zip(**arguments))