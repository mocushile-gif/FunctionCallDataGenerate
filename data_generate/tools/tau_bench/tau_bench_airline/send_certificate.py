from typing import Any, Dict
import os
import json
from dotenv import load_dotenv
load_dotenv()

def send_certificate(
    user_id: str,
    amount: int) -> str:

    with open('airline.json','r',encoding='utf-8') as f:
        data=json.load(f)
    users = data["users"]
    if user_id not in users:
        return "Error: user not found"
    user = users[user_id]

    # add a certificate, assume at most 3 cases per task
    for id in [3221322, 3221323, 3221324]:
        payment_id = f"certificate_{id}"
        if payment_id not in user["payment_methods"]:
            user["payment_methods"][payment_id] = {
                "source": "certificate",
                "amount": amount,
                "id": payment_id,
            }
            with open('airline.json','w',encoding='utf-8') as f:
                f.write(json.dumps(data,ensure_ascii=False,indent=4))
            return f"Certificate {payment_id} added to user {user_id} with amount {amount}."


# Example usage:
if __name__ == "__main__":
    os.chdir(os.environ.get("TAU_BENCH_DATA_PATH"))
    arguments={"user_id": "noah_muller_9847", "amount": 50}
    print(send_certificate(**arguments))