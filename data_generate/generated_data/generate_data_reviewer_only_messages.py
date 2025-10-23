import json
import os

def generate_data_view_html(messages_str):
    html_template = f"""<!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>JSON Data Viewer</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/prism.min.js"></script>
        <link href="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/themes/prism-tomorrow.min.css" rel="stylesheet">
        <style>
            body {{
                padding: 20px;
            }}
            .container {{
                max-width: 1000px;
                margin: auto;
                position: relative;
            }}
            .json-container {{
                background: #2d2d2d;
                padding: 15px;
                border-radius: 5px;
                color: #ffffff;
                font-family: "Courier New", monospace;
                white-space: pre-wrap;
                overflow-x: auto;
                height: 500px;
                overflow-y: auto;
                width: 1000px;
            }}
            .message-container {{
                width: 1000px;
            }}
            .json-key {{ color: #f8c555; }}
            .json-string {{ color: #a5e844; }}
            .json-number {{ color: #66d9ef; }}
            .json-boolean {{ color: #ff79c6; }}
            .json-null {{ color: #bd93f9; }}
            .button-group {{
                display: flex;
                justify-content: space-between;
                margin-top: 10px;
            }}
            .current-index {{
                text-align: center;
                font-weight: bold;
                margin-top: 20px;
            }}
        </style>
    </head>
    <body>

        <div class="container">
            <h2 class="text-center">JSON Data Viewer</h2>

            <div class="button-group">
                <button class="btn btn-secondary" onclick="prevEntry()">Previous</button>
                <button class="btn btn-primary" onclick="nextEntry()">Next</button>
            </div>

            <div class="current-index">
                <span>Current Index: <span id="current-index">0</span> / <span id="total-index">{len(json.loads(messages_str))}</span></span>
            </div>

            <div>
                <div class="json-container message-container">
                    <pre><code id="messages-display" class="language-json"></code></pre>
                </div>
            </div>
        </div>

        <script>
            const messagesData = {messages_str};  
            let currentIndex = 0;

            function syntaxHighlight(json) {{
                if (typeof json !== 'string') {{
                    json = JSON.stringify(json, null, 4);
                }}
                json = json.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
                return json.replace(/("(\\u[a-zA-Z0-9]{{4}}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false|null)\b|-?\\d+(\\.\\d*)?([eE][+-]?\\d+)?)/g, function(match) {{
                    let cls = 'json-number';
                    if (/^"/.test(match)) {{
                        if (/:$/.test(match)) {{
                            cls = 'json-key';
                        }} else {{
                            cls = 'json-string';
                        }}
                    }} else if (/true|false/.test(match)) {{
                        cls = 'json-boolean';
                    }} else if (/null/.test(match)) {{
                        cls = 'json-null';
                    }}
                    return '<span class="' + cls + '">' + match + '</span>';
                }});
            }}

            function updateDisplay() {{
                const messagesElement = document.getElementById("messages-display");
                const currentIndexElement = document.getElementById("current-index");
                const totalIndexElement = document.getElementById("total-index");

                messagesElement.innerHTML = syntaxHighlight(messagesData[currentIndex]); // Apply highlighting
                currentIndexElement.textContent = currentIndex; 
                totalIndexElement.textContent = messagesData.length; 
            }}

            function nextEntry() {{
                if (currentIndex < messagesData.length - 1) {{
                    currentIndex++;
                    updateDisplay();
                }}
            }}

            function prevEntry() {{
                if (currentIndex > 0) {{
                    currentIndex--;
                    updateDisplay();
                }}
            }}

            updateDisplay();
        </script>

    </body>
    </html>
    """
    return html_template






if __name__ == "__main__":
    # File Paths
    project_path = '/mnt/nvme0/qinxinyi/function_call_data/data_generate/generated_data/executable_tools'
    data_path = os.path.join(project_path, 'transfer_toolace_format/executable_tools_sample_800.jsonl')
    output_path = os.path.join(project_path, 'data_reviewer_executable_800.html')
    
    project_path = '/mnt/nvme0/qinxinyi/function_call_data/data_generate/generated_data/toolace'
    data_path = os.path.join(project_path, 'toolace_data_transformed_shuf_800.jsonl')
    output_path = os.path.join(project_path, 'data_reviewer_toolace.html')

    json_data = []

    # Read JSONL or JSON
    with open(data_path, 'r', encoding='utf-8') as f:
        if data_path.endswith('.jsonl'):
            for line in f:
                json_data.append(json.loads(line.strip(), strict=False))
        elif data_path.endswith('.json'):
            json_data = json.load(f)

    messages=[{'messages':data[1:]} for data in json_data if "alert(" not in str(data) and '<html>' not in str(data)]
    messages_str = json.dumps(messages, indent=4)
    print(messages_str[0])
    # Save the generated HTML file
    with open(output_path, "w", encoding="utf-8") as f:
        html_content = generate_data_view_html(messages_str)
        f.write(html_content)

    print(f"Data Reviewer HTML file has been created: {output_path}")
