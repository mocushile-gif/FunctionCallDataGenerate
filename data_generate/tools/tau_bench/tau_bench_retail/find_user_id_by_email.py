from typing import Any, Dict
import json
import os
from dotenv import load_dotenv
load_dotenv()

def find_user_id_by_email(email: str) -> str:

    with open('retail.json','r',encoding='utf-8') as f:
        data=json.load(f)

    users = data["users"]
    for user_id, profile in users.items():
        if profile["email"].lower() == email.lower():
            return user_id
    return "Error: user not found"

# Example usage:
if __name__ == "__main__":
    os.chdir(os.environ.get("TAU_BENCH_DATA_PATH"))
    arguments={'email': 'noah.brown7922@example.com'}
    print(find_user_id_by_email(**arguments))