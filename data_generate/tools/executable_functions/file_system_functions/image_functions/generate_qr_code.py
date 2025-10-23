import os
import json
from typing import Dict, Any, Optional
from dotenv import load_dotenv
import qrcode
from PIL import Image
load_dotenv()

def generate_qr_code(data: str, output_path: Optional[str] = None, 
                     size: int = 10, border: int = 4, 
                     fill_color: str = "black", back_color: str = "white"):
    """
    Generate QR code from text data.

    Parameters:
    - data (str): Text data to encode in QR code.
    - output_path (str, optional): Path for the output QR code image. If not provided, will create auto-named file.
    - size (int): Size of each QR code module in pixels (1-20).
    - border (int): Border size around QR code in modules (0-10).
    - fill_color (str): Color of QR code modules (hex color or color name).
    - back_color (str): Background color (hex color or color name).

    Returns:
    - dict: Processing result information.
    """
    
    try:
        # Validate parameters
        if not data or len(data.strip()) == 0:
            return {"error": "Data cannot be empty"}
        
        if size < 1 or size > 20:
            return {"error": "size must be between 1 and 20"}
        
        if border < 0 or border > 10:
            return {"error": "border must be between 0 and 10"}
        
        # Set output path if not provided
        if output_path is None:
            output_path = "qr_code.png"
        
        # Check if required libraries are available
        try:
            
            # Create QR code instance
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=size,
                border=border
            )
            
            # Add data to QR code
            qr.add_data(data)
            qr.make(fit=True)
            
            # Create QR code image
            qr_image = qr.make_image(fill_color=fill_color, back_color=back_color)
            
            # Save the QR code image
            qr_image.save(output_path)
            
            # Get output file information
            output_size = os.path.getsize(output_path)
            
            # Get QR code information
            qr_info = {
                "version": qr.version,
                "box_count": qr.modules_count,
                "data_length": len(data),
                "error_correction_level": "L"
            }
            
            result = {
                "data": data,
                "output_path": output_path,
                "operation": "generate_qr_code",
                "parameters": {
                    "size": size,
                    "border": border,
                    "fill_color": fill_color,
                    "back_color": back_color
                },
                "qr_code_info": qr_info,
                "output_file_size": output_size,
                "success": True
            }
            
            return result
            
        except ImportError:
            return {"error": "qrcode and PIL (Pillow) libraries are required for QR code generation"}
            
    except Exception as e:
        return {"error": f"Error generating QR code: {str(e)}"}

if __name__ == "__main__":
    # Example usage
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    result = generate_qr_code("https://www.example.com", size=10, border=4)
    print(json.dumps(result, indent=2)) 