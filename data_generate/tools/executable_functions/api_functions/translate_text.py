import os
import json
from typing import Dict, Any, Optional
from deep_translator import GoogleTranslator
from dotenv import load_dotenv
load_dotenv()

def translate_text(text: str, target_language: str = "en", source_language: str = None,
                   output_path: Optional[str] = None):
    """
    Translate text to target language.

    Parameters:
    - text (str): Text to translate.
    - target_language (str): Target language code (e.g., "en", "zh", "ja", "ko", "fr", "de", "es").
    - source_language (str, optional): Source language code. If not provided, will auto detect the source language.
    - output_path (str, optional): Path for the output translated text file. If not provided, will create auto-named file.

    Returns:
    - dict: Processing result information including translated text.
    """
    try:
        # Validate parameters
        if not text or len(text.strip()) == 0:
            return {"error": "Text cannot be empty"}
        
        # Set output path if not provided
        if output_path is None:
            output_path = f"translated_text_{target_language}.txt"
            
        # Create translator instance
        if source_language:
            translator = GoogleTranslator(
                source=source_language, 
                target=target_language)
        else:
            translator = GoogleTranslator(
                target=target_language) 

        # Translate text
        translation = translator.translate(
            text
        )

        # Get translation details
        translated_text = translation
        
        # Save translated text to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(translated_text)
        
        # Get output file information
        output_size = os.path.getsize(output_path)
        
        result = {
            "original_text": text,
            "translated_text": translated_text,
            "output_path": output_path,
            "text_statistics": {
                "original_length": len(text),
                "translated_length": len(translated_text),
                "word_count": len(text.split()),
                "translated_word_count": len(translated_text.split())
            },
            "output_file_size": output_size,
            "success": True
        }
        
        return result
            
    except Exception as e:
        return {"error": f"Error translating text: {str(e)}"}

if __name__ == "__main__":
    # Example usage
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    # result = translate_text("Hello, how are you?", target_language="zh-CN", source_language="en")
    result = translate_text("Hello, how are you?", target_language="zh-CN")
    print(json.dumps(result, indent=2)) 