import os
import json
import pandas as pd
from dotenv import load_dotenv
load_dotenv()


def convert_json_to_csv(input_path, output_path):
    """
    Convert between JSON/JSONL and CSV formats based on file extensions.

    Parameters:
    - input_path (str): Input file path (.json, .jsonl, .csv)
    - output_path (str): Output file path (.csv, .json, or .jsonl)

    Returns:
    - (bool, str): Success status and message
    """

    try:
        input_ext = os.path.splitext(input_path)[1].lower()
        output_ext = os.path.splitext(output_path)[1].lower()

        # JSON/JSONL → CSV
        if input_ext in [".json", ".jsonl"] and output_ext == ".csv":
            data = []
            with open(input_path, "r", encoding="utf-8") as f:
                if input_ext == ".jsonl":
                    for line in f:
                        data.append(json.loads(line.strip()))
                else:
                    data = json.load(f)
                    if isinstance(data, dict):
                        data = [data]

            if not isinstance(data, list):
                return False, "Error: JSON is not a list of dictionaries."

            df = pd.DataFrame(data)
            df.to_csv(output_path, index=False, encoding="utf-8")
            return True, f"Converted {input_ext} to CSV: {output_path}"

        # CSV → JSON/JSONL
        elif input_ext == ".csv" and output_ext in [".json", ".jsonl"]:
            df = pd.read_csv(input_path)
            records = df.to_dict(orient="records")
            with open(output_path, "w", encoding="utf-8") as f:
                if output_ext == ".json":
                    json.dump(records, f, ensure_ascii=False, indent=2)
                else:  # .jsonl
                    for row in records:
                        f.write(json.dumps(row, ensure_ascii=False) + "\n")
            return True, f"Converted CSV to {output_ext}: {output_path}"

        else:
            return False, f"Unsupported conversion: {input_ext} → {output_ext}"

    except Exception as e:
        return False, f"Error: {str(e)}"


# Example usage
if __name__ == "__main__":
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    # JSON → CSV
    success, msg = convert_json_to_csv("json_data/Books.json", "converted_data.csv")
    print(success, msg)

    # CSV → JSON
    success, msg = convert_json_to_csv("converted_data.csv", "converted_output.json")
    print(success, msg)

    # CSV → JSONL
    success, msg = convert_json_to_csv("converted_data.csv", "converted_output.jsonl")
    print(success, msg)
