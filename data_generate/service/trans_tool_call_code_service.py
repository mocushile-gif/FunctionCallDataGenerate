# file: api_server.py
from flask import Flask, request, jsonify
from data_generate.service.trans_tool_call_code import generate_tool_call_code

app = Flask(__name__)

@app.route("/fc2code", methods=["POST"])
def fc2code_service():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing assistant_message"}), 400

    try:
        code = generate_tool_call_code(data["assistant_message"])
        return jsonify({"code": code})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)

# curl -X POST http://101.230.144.221:22222/fc2code \
#   -H "Content-Type: application/json" \
#   -d '{
#     "assistant_message": {
#       "role": "assistant",
#       "tool_calls": [
#         {
#           "function": {
#             "name": "display_directory_tree",
#             "arguments": {
#               "path": "./",
#               "depth": 2
#             }
#           },
#           "id": "call_fake_id",
#           "type": "function"
#         }
#       ]
#     }
#   }'

