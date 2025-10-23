import requests
import os
from dotenv import load_dotenv
load_dotenv()

def get_top_n_personas(tools,n):
    url = f"http://{os.environ['PERSONA_URL']}/get_top_n_personas"
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "tools": tools,
        "n": n
    }

    response = requests.post(url, headers=headers, json=data, timeout=10)
    if response.status_code == 200:
        out = response.json().get('res')
        return out
    else:
        # print(response.json())
        raise Exception(f"Error: {response.json().get('error')}")
    
tools = [
    {"name": "execute_sql_command", "description": "Executes an SQL query on the specified SQLite database."},
    {"name": "change_owner", "description": "Change the owner and group of a file or directory."}
]

res=get_top_n_personas(tools,10)
print(res)