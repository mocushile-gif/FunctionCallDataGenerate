import os
import json
from typing import Dict, Any, Optional
from dotenv import load_dotenv
load_dotenv()

def summarize_text(text: str, max_length: int = 300, method: str = "extractive",
                   output_path: Optional[str] = None):
    """
    Generate a summary of the input text.

    Parameters:
    - text (str): Text to summarize.
    - max_length (int): Maximum length of summary in characters (50-500).
    - method (str): Summarization method. Options: "extractive", "abstractive".
    - output_path (str, optional): Path for the output summary file. If not provided, will create auto-named file.

    Returns:
    - dict: Processing result information including summary.
    """
    try:
        # Validate parameters
        if not text or len(text.strip()) == 0:
            return {"error": "Text cannot be empty"}
        
        if max_length < 50 or max_length > 1000:
            return {"error": "max_length must be between 50 and 1000"}
        
        if method not in ["extractive", "abstractive"]:
            return {"error": "method must be one of: extractive, abstractive"}
        
        # Set output path if not provided
        if output_path is None:
            output_path = "text_summary.txt"
        
        # Check if required libraries are available
        try:
            import re
            from collections import Counter
            
            # Simple extractive summarization using TF-IDF approach
            def extractive_summarize(text, max_length):
                # Clean and tokenize text
                sentences = re.split(r'[.!?]+', text)
                sentences = [s.strip() for s in sentences if s.strip()]
                
                if not sentences:
                    return text[:max_length]
                
                # Calculate word frequencies
                words = re.findall(r'\b\w+\b', text.lower())
                word_freq = Counter(words)
                
                # Calculate sentence scores based on word frequency
                sentence_scores = {}
                for sentence in sentences:
                    sentence_words = re.findall(r'\b\w+\b', sentence.lower())
                    score = sum(word_freq[word] for word in sentence_words)
                    sentence_scores[sentence] = score
                
                # Sort sentences by score
                sorted_sentences = sorted(sentence_scores.items(), key=lambda x: x[1], reverse=True)
                
                # Build summary
                summary = ""
                for sentence, score in sorted_sentences:
                    if len(summary + sentence) <= max_length:
                        summary += sentence + ". "
                    else:
                        break
                
                return summary.strip()
            
            # Abstractive summarization using Hugging Face API
            def abstractive_summarize(text, max_length):
                try:
                    import requests
                    
                    # Check if HF_TOKEN is available
                    api_key = os.getenv("ZHIPU_API_KEY")
                    if not api_key:
                        print("ZHIPU_API_KEY not found in environment variables.")
                        return extractive_summarize(text, max_length)
                    
                    # Hugging Face API endpoint
                    API_URL = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
                    headers = {
                        "Authorization": f"Bearer {api_key}",
                    }
                    message=messages = [
                                {
                                    "role": "user",
                                    "content": f"""Please summarize the following text into a JSON object with the key `summary`, ensuring the summary does not exceed {max_length} characters.

                            Text:
                            {text}

                            Respond in this JSON format:
                            {{"summary": "<your summary here>"}}
                            """
                                }
                            ]

                    payload = {
                        "model": "glm-4v-flash",
                        "messages": messages
                    }
                    response = requests.post(
                        API_URL,
                        headers={
                            "Content-Type": "application/json",
                            "Authorization": f"Bearer {api_key}"
                        },
                        data=json.dumps(payload)
                    )
                    response.raise_for_status()
                    data = response.json()
                    summary = data["choices"][0]["message"]["content"]
                    print(summary)
                    try:
                        if '```json' in summary:
                            match = re.findall(r'```json\s*(.*?)\s*```', summary, re.DOTALL)[0]
                            summary=json.loads(match,strict=False)['summary']
                        else:
                            summary = json.loads(summary)['summary']
                    except:
                        pass
                    
                    return summary
                    
                except Exception as e:
                    print(f"Abstractive summarization failed: {e}, falling back to extractive")
                    return extractive_summarize(text, max_length)
            
            # Generate summary
            if method == "extractive":
                summary = extractive_summarize(text, max_length)
            else:
                summary = abstractive_summarize(text, max_length)
         
            # Save summary to file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(summary)
            
            # Get output file information
            output_size = os.path.getsize(output_path)
            
            # Calculate compression ratio
            compression_ratio = len(summary) / len(text) if len(text) > 0 else 0
            
            result = {
                "original_text": text,
                "summary": summary,
                "output_path": output_path,
                "parameters": {
                    "max_length": max_length,
                    "method": method
                },
                "summary_statistics": {
                    "original_length": len(text),
                    "summary_length": len(summary),
                    "compression_ratio": round(compression_ratio, 3),
                    "original_word_count": len(text.split()),
                    "summary_word_count": len(summary.split())
                },
                "output_file_size": output_size,
                "success": True
            }
            
            return result
            
        except ImportError:
            return {"error": "Required libraries not available for text summarization"}
            
    except Exception as e:
        return {"error": f"Error summarizing text: {str(e)}"}

if __name__ == "__main__":
    # Example usage
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    sample_text = """
    Artificial intelligence (AI) is intelligence demonstrated by machines, in contrast to the natural intelligence displayed by humans and animals. Leading AI textbooks define the field as the study of "intelligent agents": any device that perceives its environment and takes actions that maximize its chance of successfully achieving its goals. Colloquially, the term "artificial intelligence" is often used to describe machines (or computers) that mimic "cognitive" functions that humans associate with the human mind, such as "learning" and "problem solving".
    """
    result = summarize_text(sample_text, max_length=200, method="abstractive")
    print(json.dumps(result, indent=2)) 