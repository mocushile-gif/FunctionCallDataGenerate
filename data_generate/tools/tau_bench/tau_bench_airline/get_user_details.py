import json
from typing import Any, Dict
import os
from dotenv import load_dotenv
load_dotenv()

def get_user_details(user_id: str) -> str:

    with open('airline.json','r',encoding='utf-8') as f:
        data=json.load(f)
    users = data["users"]
    if user_id in users:
        return json.dumps(users[user_id])
    return "Error: user not found"


# Example usage:
if __name__ == "__main__":
    os.chdir(os.environ.get("TAU_BENCH_DATA_PATH"))
    arguments={
              "user_id": "olivia_gonzalez_2305"
            }
    print(get_user_details(**arguments))