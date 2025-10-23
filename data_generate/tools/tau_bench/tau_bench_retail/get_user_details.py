# Copyright Sierra

import json
import os
from typing import Any, Dict
from dotenv import load_dotenv
load_dotenv()

def get_user_details(user_id: str) -> str:

    with open('retail.json','r',encoding='utf-8') as f:
        data=json.load(f)

    users = data["users"]
    if user_id in users:
        return json.dumps(users[user_id])
    return "Error: user not found"

# Example usage:
if __name__ == "__main__":
    os.chdir(os.environ.get("TAU_BENCH_DATA_PATH"))
    print(get_user_details('james_li_5688'))