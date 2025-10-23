import os
import json
from typing import Dict, Any, Optional
from dotenv import load_dotenv
load_dotenv()

def extract_text_from_image(image_path: str, language: str = "eng", 
                           output_path: Optional[str] = None):
    """
    Extract text from image using OCR (Optical Character Recognition).

    Parameters:
    - image_path (str): Path to the input image file.
    - language (str): Language code for OCR. Options: "eng", "chi_sim", "chi_tra", "jpn", "kor", etc.
    - output_path (str, optional): Path for the output text file. If not provided, will create auto-named file.

    Returns:
    - dict: Processing result information including extracted text.
    """
    
    
    try:
        # Check if input file exists
        if not os.path.exists(image_path):
            return {"error": f"Input image file not found: {image_path}"}
        
        # Validate parameters
        supported_languages = ["eng", "chi_sim", "chi_tra", "jpn", "kor", "fra", "deu", "spa", "rus", "ara"]
        if language not in supported_languages:
            return {"error": f"language must be one of: {', '.join(supported_languages)}"}
        
        # Set output path if not provided
        if output_path is None:
            base_name = os.path.splitext(image_path)[0]
            output_path = f"{base_name}_extracted_text.txt"
        
        # Get file information
        file_size = os.path.getsize(image_path)
        
        # Check if required libraries are available
        try:
            import pytesseract
            from PIL import Image
            
            # Open the image
            with Image.open(image_path) as img:
                original_size = img.size
                original_mode = img.mode
                
                # Extract text using OCR
                extracted_text = pytesseract.image_to_string(img, lang=language)
                
                # Save extracted text to file
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(extracted_text)
                
                # Get output file information
                output_size = os.path.getsize(output_path)
                
                # Get confidence scores if available
                try:
                    data = pytesseract.image_to_data(img, lang=language, output_type=pytesseract.Output.DICT)
                    confidence_scores = [score for score in data['conf'] if score > 0]
                    avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
                except:
                    avg_confidence = None
                
                # Count words and characters
                word_count = len(extracted_text.split())
                char_count = len(extracted_text)
                
                result = {
                    "input_path": image_path,
                    "output_path": output_path,
                    "operation": "extract_text_from_image",
                    "parameters": {
                        "language": language
                    },
                    "original_size": original_size,
                    "original_mode": original_mode,
                    "input_file_size": file_size,
                    "output_file_size": output_size,
                    "extracted_text": extracted_text,
                    "text_statistics": {
                        "word_count": word_count,
                        "character_count": char_count,
                        "average_confidence": avg_confidence
                    },
                    "success": True
                }
                
                return result
                
        except ImportError:
            return {"error": "pytesseract and PIL (Pillow) libraries are required for OCR"}
            
    except Exception as e:
        return {"error": f"Error extracting text: {str(e)}"}

if __name__ == "__main__":
    # Example usage
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    result = extract_text_from_image("./image_data/chat.png", language="eng")
    print(json.dumps(result, indent=2)) 