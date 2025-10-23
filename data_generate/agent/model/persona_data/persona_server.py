from flask import Flask, request, jsonify
from FlagEmbedding import BGEM3FlagModel
import torch
import json
import pickle
import os

class Persona:
    def __init__(self, persona_data_path, persona_embeddings_path):
        # 使用 GPU
        self.device = 'cuda:0' if torch.cuda.is_available() else 'cpu'
        
        self.model = BGEM3FlagModel("/mnt/afs2/qinxinyi/model/bge-m3", devices=self.device)
        # self.model = BGEM3FlagModel('BAAI/bge-m3', devices=self.device)

        # 加载 Persona 数据
        self.persona_data = []
        with open(persona_data_path, "r", encoding="utf-8") as f:
            for line in f:
                self.persona_data.append(json.loads(line)["persona"])

        # 加载或生成嵌入
        if os.path.exists(persona_embeddings_path):
            with open(persona_embeddings_path, "rb") as f:
                self.persona_embeddings = torch.tensor(pickle.load(f)).to(self.device)
        else:
            self.persona_embeddings = self.persona_init(persona_embeddings_path)

    def persona_init(self, persona_embeddings_path):
        embeddings = self.model.encode(self.persona_data, batch_size=256, max_length=512)['dense_vecs']
        with open(persona_embeddings_path, "wb") as f:
            pickle.dump(embeddings, f)
        return torch.tensor(embeddings).to(self.device)

    def get_top_n_personas(self, tools, n):
        # 构建工具描述
        tool_descriptions = [f"name: {tool['name']}\ndescription: {tool['description']}" for tool in tools]
        # 生成工具嵌入（转为 torch.Tensor 并搬到 GPU）
        tool_embeddings_np = self.model.encode(tool_descriptions)['dense_vecs']
        tool_embeddings = torch.tensor(tool_embeddings_np).to(self.device)

        # 计算相似度（矩阵乘法）
        similarities = torch.matmul(tool_embeddings, self.persona_embeddings.T)
        cumulative_similarities = similarities.sum(dim=0)

        # 获取 Top-N
        top_n_indices = torch.topk(cumulative_similarities, n).indices.tolist()
        top_n_personas = [self.persona_data[i] for i in top_n_indices]
        return top_n_personas


# 路径配置
import data_generate

project_dir = os.path.dirname(data_generate.__file__)
persona_data_path = f"{project_dir}/agent/model/persona_data/persona.jsonl"
persona_embeddings_path = f"{project_dir}/agent/model/persona_data/persona_embeddings.pkl"
persona_instance = Persona(persona_data_path, persona_embeddings_path)

# 启动 Flask 服务
app = Flask(__name__)

@app.route('/get_top_n_personas', methods=['POST'])
def get_top_n_personas():
    data = request.json
    tools = data.get('tools', [])
    n = data.get('n', 3)
    try:
        result = persona_instance.get_top_n_personas(tools, n)
        return jsonify({'res': result})
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
