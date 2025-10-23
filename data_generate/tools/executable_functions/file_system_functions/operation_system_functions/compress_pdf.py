import os
import json
from typing import Dict, Any, Optional
from dotenv import load_dotenv
load_dotenv()

def compress_pdf(input_path: str, output_path: str = None, 
                 compression_level: str = "medium", 
                 image_quality: int = 85,
                 remove_metadata: bool = False,
                 ):
    """
    Compress a PDF file to reduce file size.
    
    Parameters:
    - input_path (str): Path to input PDF file
    - output_path (str): Path for output file (optional, auto-generated if not provided)
    - compression_level (str): Compression level ("low", "medium", "high", "extreme")
    - image_quality (int): Image quality for compression (1-100)
    - remove_metadata (bool): Whether to remove metadata
    
    Returns:
    - dict: Compression result information
    """
    
    
    try:
        # Validate parameters
        if not input_path or not os.path.exists(input_path):
            return {"error": "Input PDF file not found"}
        
        if not input_path.lower().endswith('.pdf'):
            return {"error": "Input file must be a PDF"}
        
        if compression_level not in ["low", "medium", "high", "extreme"]:
            return {"error": "Compression level must be 'low', 'medium', 'high', or 'extreme'"}
        
        if image_quality < 1 or image_quality > 100:
            return {"error": "Image quality must be between 1 and 100"}
        
        # Import required libraries
        try:
            import fitz  # PyMuPDF
            from PIL import Image
            import io
        except ImportError:
            return {"error": "Required libraries not available. Install: pip install PyMuPDF Pillow"}
        
        # Set output path if not provided
        if not output_path:
            base_name = os.path.splitext(os.path.basename(input_path))[0]
            output_path = f"{base_name}_compressed.pdf"
        
        # Open PDF
        doc = fitz.open(input_path)
        
        # Compression settings based on level
        compression_settings = {
            "low": {"image_quality": 95, "image_dpi": 150, "clean": True},
            "medium": {"image_quality": 85, "image_dpi": 120, "clean": True},
            "high": {"image_quality": 70, "image_dpi": 100, "clean": True},
            "extreme": {"image_quality": 50, "image_dpi": 72, "clean": True}
        }
        
        settings = compression_settings[compression_level]
        
        # Process each page
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            
            # Get image list
            image_list = page.get_images()
            
            for img_index, img in enumerate(image_list):
                try:
                    # Get image
                    xref = img[0]
                    pix = fitz.Pixmap(doc, xref)
                    
                    # Convert to PIL Image for compression
                    img_data = pix.tobytes("png")
                    pil_image = Image.open(io.BytesIO(img_data))
                    
                    # Compress image
                    compressed_img_data = io.BytesIO()
                    pil_image.save(compressed_img_data, format="JPEG", 
                                 quality=settings["image_quality"], 
                                 optimize=True)
                    
                    # Replace image in PDF
                    compressed_img_data.seek(0)
                    doc.update_stream(xref, compressed_img_data.getvalue())
                    
                    pix = None  # Free memory
                    
                except Exception as e:
                    print(f"Warning: Could not compress image {img_index} on page {page_num + 1}: {e}")
                    continue
        
        # Save compressed PDF
        save_options = {
            "garbage": 4,  # Remove unused objects
            "deflate": True,  # Use deflate compression
            "clean": settings["clean"],  # Clean PDF structure
            "ascii": False,  # Binary output
            "pretty": False,  # No pretty printing
        }
        
        if remove_metadata:
            # Remove metadata
            doc.set_metadata({})
        
        doc.save(output_path, **save_options)
        doc.close()
        
        # Calculate compression results
        original_size = os.path.getsize(input_path)
        compressed_size = os.path.getsize(output_path)
        compression_ratio = round(compressed_size / original_size, 3)
        size_reduction = round((1 - compression_ratio) * 100, 2)
        
        result = {
            "input_file": input_path,
            "output_path": output_path,
            "compression_level": compression_level,
            "image_quality": settings["image_quality"],
            "remove_metadata": remove_metadata,
            "original_size": original_size,
            "compressed_size": compressed_size,
            "compression_ratio": compression_ratio,
            "size_reduction_percent": size_reduction,
            "success": True
        }
        
        # Add compression efficiency
        if size_reduction > 0:
            result["compression_efficiency"] = "good"
        elif size_reduction > -10:  # Less than 10% size increase
            result["compression_efficiency"] = "acceptable"
        else:
            result["compression_efficiency"] = "poor"
        
        return result
        
    except Exception as e:
        return {"error": f"Error compressing PDF: {str(e)}"}

if __name__ == "__main__":
    # Example usage
    result = compress_pdf("./pdf_data/order.pdf", compression_level="high", remove_metadata=True)
    print(json.dumps(result, indent=2)) 
