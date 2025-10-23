import os
import json
from typing import Dict, Any, Optional
from dotenv import load_dotenv
load_dotenv()

def encrypt_decrypt_pdf(input_path: str, output_path: str = None, 
                       operation: str = "encrypt", password: str = "",
                       encryption_level: str = "AES-256", 
                       permissions: Optional[Dict[str, bool]] = None,
                       ):
    """
    Encrypt or decrypt a PDF file.
    
    Parameters:
    - input_path (str): Path to input PDF file
    - output_path (str): Path for output file (optional, auto-generated if not provided)
    - operation (str): "encrypt" or "decrypt"
    - password (str): Password for encryption/decryption
    - encryption_level (str): Encryption level ("AES-256", "AES-128", "RC4-128")
    - permissions (dict): PDF permissions (print, copy, modify, etc.)
    
    Returns:
    - dict: Encryption/decryption result information
    """

    try:
        # Validate parameters
        if not input_path or not os.path.exists(input_path):
            return {"error": "Input PDF file not found"}
        
        if not input_path.lower().endswith('.pdf'):
            return {"error": "Input file must be a PDF"}
        
        if operation not in ["encrypt", "decrypt"]:
            return {"error": "Operation must be 'encrypt' or 'decrypt'"}
        
        if operation == "encrypt" and not password:
            return {"error": "Password is required for encryption"}
        
        if encryption_level not in ["AES-256", "AES-128", "RC4-128"]:
            return {"error": "Encryption level must be 'AES-256', 'AES-128', or 'RC4-128'"}
        
        # Import required libraries
        try:
            from PyPDF2 import PdfReader, PdfWriter
            from PyPDF2.constants import PageAttributes as PG
        except ImportError:
            return {"error": "Required libraries not available. Install: pip install PyPDF2"}
        
        # Set default permissions
        if permissions is None:
            permissions = {
                "print": True,
                "copy": False,
                "modify": False,
                "annotate": False,
                "fill_forms": False,
                "extract_text": False,
                "assemble": False,
                "print_high_resolution": False
            }
        
        # Set output path if not provided
        if not output_path:
            base_name = os.path.splitext(os.path.basename(input_path))[0]
            if operation == "encrypt":
                output_path = f"{base_name}_encrypted.pdf"
            else:
                output_path = f"{base_name}_decrypted.pdf"
        
        # Read input PDF
        reader = PdfReader(input_path)
        
        # Check if PDF is already encrypted/decrypted
        if operation == "encrypt" and reader.is_encrypted:
            return {"error": "PDF is already encrypted"}
        
        if operation == "decrypt" and not reader.is_encrypted:
            return {"error": "PDF is not encrypted"}
        
        # Perform operation
        if operation == "encrypt":
            # Encrypt PDF
            writer = PdfWriter()
            
            # Add all pages
            for page in reader.pages:
                writer.add_page(page)
            
            # Set encryption
            writer.encrypt(
                user_pwd=password,
                owner_pwd=password,
                use_128bit=True if "AES-128" in encryption_level else False,
                permissions_flag=calculate_permissions_flag(permissions)
            )
            
            # Write encrypted PDF
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
            
            result = {
                "operation": "encrypt",
                "input_file": input_path,
                "output_path": output_path,
                "encryption_level": encryption_level,
                "permissions": permissions,
                "success": True
            }
            
        else:
            # Decrypt PDF
            try:
                reader.decrypt(password)
            except Exception as e:
                return {"error": f"Failed to decrypt PDF: {str(e)}"}
            
            writer = PdfWriter()
            
            # Add all pages
            for page in reader.pages:
                writer.add_page(page)
            
            # Write decrypted PDF
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
            
            result = {
                "operation": "decrypt",
                "input_file": input_path,
                "output_path": output_path,
                "success": True
            }
        
        # Add common information
        result.update({
            "input_size": os.path.getsize(input_path),
            "output_size": os.path.getsize(output_path)
        })
        result.update({
            "compression_ratio": round(result["output_size"] / result["input_size"], 3)
        })
        
        return result
        
    except Exception as e:
        return {"error": f"Error in PDF {operation}: {str(e)}"}

def calculate_permissions_flag(permissions: Dict[str, bool]) -> int:
    """
    Calculate permissions flag for PDF encryption.
    
    Parameters:
    - permissions (dict): Dictionary of permission settings
    
    Returns:
    - int: Permissions flag
    """
    flag = 0
    
    # PDF permissions mapping
    permission_map = {
        "print": 0b00000000000000000000000000000001,
        "modify": 0b00000000000000000000000000000010,
        "copy": 0b00000000000000000000000000000100,
        "annotate": 0b00000000000000000000000000001000,
        "fill_forms": 0b00000000000000000000000000010000,
        "extract_text": 0b00000000000000000000000000100000,
        "assemble": 0b00000000000000000000000001000000,
        "print_high_resolution": 0b00000000000000000000000010000000
    }
    
    for permission, enabled in permissions.items():
        if enabled and permission in permission_map:
            flag |= permission_map[permission]
    
    return flag

if __name__ == "__main__":
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    # Example usage
    result = encrypt_decrypt_pdf("./pdf_data/order.pdf", operation="encrypt", password="mypassword123")
    result = encrypt_decrypt_pdf("order_encrypted.pdf", operation="decrypt", password="mypassword123")
    print(json.dumps(result, indent=2)) 