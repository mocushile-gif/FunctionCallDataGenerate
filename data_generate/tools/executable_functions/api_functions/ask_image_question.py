import os
import json
import base64
import requests
from typing import Optional
from dotenv import load_dotenv
load_dotenv()

def ask_image_question(image_path: str,
                       question: str,
                       max_tokens: int = 300,
                       output_path: Optional[str] = None) -> dict:
    """
    Ask a question about an image using Zhipu GLM-4V vision model.

    Parameters:
    - image_path (str): Local path to the image file.
    - question (str): The question to ask about the image.
    - max_tokens (int): Max number of tokens in response.
    - output_path (str, optional): Optional path to save result JSON.

    Returns:
    - dict: Result including success flag, answer, and optional metadata.
    """

    if not os.path.exists(image_path):
        return {"success": False, "error": f"Image not found: {image_path}"}

    api_key = os.getenv("ZHIPU_API_KEY")
    if not api_key:
        return {"success": False, "error": "ZHIPU_API_KEY not found in environment variables."}

    # Encode image to base64
    try:
        with open(image_path, "rb") as f:
            image_base64 = base64.b64encode(f.read()).decode("utf-8")
    except Exception as e:
        return {"success": False, "error": f"Failed to read image: {str(e)}"}

    # Build request payload
    prompt_content = [
        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}},
        {"type": "text", "text": question}
    ]

    payload = {
        "model": "glm-4v-flash",
        "max_tokens": max_tokens,
        "messages": [{"role": "user", "content": prompt_content}]
    }

    try:
        response = requests.post(
            "https://open.bigmodel.cn/api/paas/v4/chat/completions",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            },
            data=json.dumps(payload)
        )
        response.raise_for_status()
        data = response.json()
        answer = data["choices"][0]["message"]["content"]

        result = {
            "success": True,
            "image_path": image_path,
            "question": question,
            "answer": answer
        }

        if output_path:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)

        return result

    except Exception as e:
        return {"success": False, "error": f"Image Q&A failed: {str(e)}"}

if __name__ == "__main__":
    # Set working directory
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    result = ask_image_question(
        image_path="./image_data/dog.jpg",
        question="What is the dog doing in this picture?",
        max_tokens=150
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
