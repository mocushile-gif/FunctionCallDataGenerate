#!/usr/bin/env python3
import json
import os

def generate_data_view_html(messages_str, metadata_str):
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
                height: 2000px;
                overflow-y: auto;
                width: 1000px;
            }}
            .message-container {{
                width: 600px;
            }}
            .metadata-container {{
                width: 400px;
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
            .split-container {{
                display: flex;
                gap: 20px;
                margin-top: 50px; /* Push content down so buttons don’t overlap */
            }}
            .split-container > div {{
                flex: 1;
            }}
            .json-title {{
                font-weight: bold;
                text-align: center;
                margin-bottom: 10px;
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

            <div class="split-container">
                <div>
                    <h5 class="json-title">Metadata</h5>
                    <div class="json-container metadata-container">
                        <pre><code id="metadata-display" class="language-json"></code></pre>
                    </div>
                </div>
                <div>
                    <h5 class="json-title">Messages</h5>
                    <div class="json-container message-container">
                        <pre><code id="messages-display" class="language-json"></code></pre>
                    </div>
                </div>
            </div>
        </div>

        <script>
            const messagesData = {messages_str};  
            const metadataData = {metadata_str};  
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
                const metadataElement = document.getElementById("metadata-display");
                const currentIndexElement = document.getElementById("current-index");
                const totalIndexElement = document.getElementById("total-index");

                messagesElement.innerHTML = syntaxHighlight(messagesData[currentIndex]);
                metadataElement.innerHTML = syntaxHighlight(metadataData[currentIndex]);
                currentIndexElement.textContent = currentIndex; // Update the current index
                totalIndexElement.textContent = messagesData.length; // Total number of entries
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

            // Initialize with the first JSON entry
            updateDisplay();
        </script>

    </body>
    </html>
    """
    return html_template





if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    project_dir=os.path.dirname(os.path.abspath(__file__))
    parser.add_argument('data_path', type=str)
    args = parser.parse_args()
    json_data = []

    # Read JSONL or JSON
    with open(args.data_path, 'r', encoding='utf-8') as f:
        if args.data_path.endswith('.jsonl'):
            for line in f:
                json_data.append(json.loads(line.strip(), strict=False))
        elif data_path.endswith('.json'):
            json_data = json.load(f)

    # Extract Messages and Metadata
    messages=[{'messages':data['messages'][1:]} for data in json_data if "alert(" not in str(data['messages']) and '<script>' not in str(data['messages']) and '</script>' not in str(data['messages'])]
    messages_str = json.dumps(messages, indent=4)

    metadata=[]
    tasks=[]
    for data in json_data:
        last_index=1
        tasks_messages={}
        task_trajectorys={}
        if "alert(" not in str(data['messages']) and '<script>' not in str(data['messages']) and '</script>' not in str(data['messages']):
            for i,task_complete_index in enumerate(data["task_complete_index"]):
                task_trajectory=[]
                task_messages=data['messages'][last_index:task_complete_index+1]
                last_index=task_complete_index+1
                tasks_messages[f"task{i}"]=task_messages
                for message in task_messages:
                    if 'tool_calls' in message:
                        tool_calls=[tool_call['function']['name'] for tool_call in message['tool_calls']]
                        task_trajectory.append(tool_calls)
                task_trajectorys[f"task{i}"]=task_trajectory
            tasks.append(tasks_messages)
            i_data={}
            i_data["task_trajectorys"]=task_trajectorys
            for k, v in data.items():
                if k=='tools':
                    i_data[k]=[tool['name'] for tool in v]
                elif k not in ['messages','assistant_reasonings']:
                    i_data[k]=v
            metadata.append(i_data)
    tasks_str = json.dumps(tasks, indent=4)
    metadata_str = json.dumps(metadata, indent=4)

    print(len(metadata))
    print(len(tasks))

    # Save the generated HTML file
    output_path = os.path.join(project_dir, 'data_reviewer.html')
    with open(output_path, "w", encoding="utf-8") as f:
        html_content = generate_data_view_html(tasks_str, metadata_str)
        f.write(html_content)

    print(f"Data Reviewer HTML file has been created: {output_path}")