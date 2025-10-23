import json
from tqdm import tqdm
import random
import pickle
import os
import requests
import torch
from dotenv import load_dotenv
load_dotenv()

class Persona:
    def __init__(self, persona_data_path, persona_embeddings_path, url=os.environ.get('PERSONA_URL', '')):
        self.persona_data_path = persona_data_path
        self.persona_embeddings_path = persona_embeddings_path

        if not url:
            from FlagEmbedding import BGEM3FlagModel
            # 使用 GPU（如果可用）
            self.device = 'cuda:0' if torch.cuda.is_available() else 'cpu'
            self.model = BGEM3FlagModel('BAAI/bge-m3', devices=self.device)

            self.persona_data = []
            with open(persona_data_path, "r", encoding="utf-8") as f:
                for line in f:
                    self.persona_data.append(json.loads(line)["persona"])

            if os.path.exists(persona_embeddings_path):
                with open(persona_embeddings_path, "rb") as f:
                    self.persona_embeddings = torch.tensor(pickle.load(f)).to(self.device)
            else:
                self.persona_embeddings = self.persona_init()
            self.use_url = False
        else:
            self.use_url = True
            self.url = f"http://{url}/get_top_n_personas"

    def persona_init(self):
        embeddings_np = self.model.encode(self.persona_data, batch_size=256, max_length=512)['dense_vecs']
        with open(self.persona_embeddings_path, "wb") as f:
            pickle.dump(embeddings_np, f)
        return torch.tensor(embeddings_np).to(self.device)

    def get_top_n_personas(self, tools, n):
        assert isinstance(tools, list)

        if not self.use_url:
            tool_descriptions = [f"name: {tool['name']}\ndescription: {tool['description']}" for tool in tools]
            tool_embeddings_np = self.model.encode(tool_descriptions)['dense_vecs']
            tool_embeddings = torch.tensor(tool_embeddings_np).to(self.device)

            # 相似度计算
            similarities = torch.matmul(tool_embeddings, self.persona_embeddings.T)
            cumulative_similarities = similarities.sum(dim=0)
            top_n_indices = torch.topk(cumulative_similarities, n).indices.tolist()
            return [self.persona_data[i] for i in top_n_indices]

        else:
            headers = {"Content-Type": "application/json"}
            data = {"tools": tools, "n": n}
            response = requests.post(self.url, headers=headers, json=data)
            if response.status_code == 200:
                return response.json().get('res')
            else:
                raise Exception(f"Error: {response.json().get('error')}")

if __name__ == '__main__':
    persona_data_path = "./agent/model/persona_data/persona.jsonl"
    persona_embeddings_path = "./agent/model/persona_data/persona_embeddings.pkl"
    persona = Persona(persona_data_path, persona_embeddings_path)

    tools = [
        {"name": "execute_sql_command", "description": "Executes an SQL query on the specified SQLite database."},
        {"name": "change_owner", "description": "Change the owner and group of a file or directory."}
    ]

    top_10_personas = persona.get_top_n_personas(tools, 10)
    print(top_10_personas)
