import os
import json
from dotenv import load_dotenv
load_dotenv()

def load_retail_data(FOLDER_PATH):
    with open(os.path.join(FOLDER_PATH, "orders.json")) as f:
        order_data = json.load(f)
    with open(os.path.join(FOLDER_PATH, "products.json")) as f:
        product_data = json.load(f)
    with open(os.path.join(FOLDER_PATH, "users.json")) as f:
        user_data = json.load(f)
    print('init tau bench retail data.')
    return {
        "orders": order_data,
        "products": product_data,
        "users": user_data,
    }

def load_airline_data(FOLDER_PATH):
    with open(os.path.join(FOLDER_PATH, "flights.json")) as f:
        flight_data = json.load(f)
    with open(os.path.join(FOLDER_PATH, "reservations.json")) as f:
        reservation_data = json.load(f)
    with open(os.path.join(FOLDER_PATH, "users.json")) as f:
        user_data = json.load(f)
    print('init tau bench airline data.')
    return {
        "flights": flight_data,
        "reservations": reservation_data,
        "users": user_data,
    }

if __name__ == "__main__":
    retail_data=load_retail_data('/afs_b/qinxinyi/tau-bench/tau_bench/envs/retail/data')
    airline_data=load_airline_data('/afs_b/qinxinyi/tau-bench/tau_bench/envs/airline/data')
    with open(os.path.join(os.environ['TAU_BENCH_DATA_PATH'],'retail.json'),'w',encoding='utf-8') as f:
        f.write(json.dumps(retail_data,ensure_ascii=False,indent=4))
    with open(os.path.join(os.environ['TAU_BENCH_DATA_PATH'],'airline.json'),'w',encoding='utf-8') as f:
        f.write(json.dumps(airline_data,ensure_ascii=False,indent=4))