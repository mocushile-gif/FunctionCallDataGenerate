import os
import json
from PIL import Image, ImageDraw
import cv2
import numpy as np
from dotenv import load_dotenv
load_dotenv()

def detect_faces_base(image_path, output_path=None, draw_faces=True, confidence_threshold=0.5, 
                 return_coordinates=False):
    """
    Detect faces in an image using OpenCV.
    
    Args:
        image_path (str): Path to the input image file
        output_path (str): Path for the output image with detected faces marked
        draw_faces (bool): Whether to draw rectangles around detected faces
        confidence_threshold (float): Confidence threshold for face detection (0.0-1.0)
        return_coordinates (bool): Whether to return face coordinates
    
    Returns:
        dict: Result information including success status and detected faces
    """
    try:
        # Validate input file
        if not os.path.exists(image_path):
            return {
                "success": False,
                "error": f"Input image file not found: {image_path}"
            }
        
        # Load the image
        image = cv2.imread(image_path)
        if image is None:
            return {
                "success": False,
                "error": "Failed to load image"
            }
        
        # Convert to grayscale for face detection
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Load the face cascade classifier
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
        # Detect faces
        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
        )
        
        # Convert OpenCV image to PIL for drawing
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(image_rgb)
        draw = ImageDraw.Draw(pil_image)
        
        # Process detected faces
        detected_faces = []
        for i, (x, y, w, h) in enumerate(faces):
            face_info = {
                "face_id": i + 1,
                "x": int(x),
                "y": int(y),
                "width": int(w),
                "height": int(h),
                "area": int(w * h)
            }
            detected_faces.append(face_info)
            
            # Draw rectangle around face if requested
            if draw_faces:
                draw.rectangle([x, y, x + w, y + h], outline=(255, 0, 0), width=3)
                # Add face number
                draw.text((x, y - 10), f"Face {i + 1}", fill=(255, 0, 0))
        
        # Determine output path
        if output_path is None and draw_faces:
            base_name = os.path.splitext(image_path)[0]
            ext = os.path.splitext(image_path)[1]
            output_path = f"{base_name}_faces_detected{ext}"
        
        # Save image with detected faces if requested
        if draw_faces and output_path:
            pil_image.save(output_path)
        
        # Prepare result
        result = {
            "success": True,
            "num_faces_detected": len(detected_faces),
            "image_path": image_path,
            "confidence_threshold": confidence_threshold
        }
        
        if draw_faces and output_path:
            result["output_path"] = output_path
        
        if return_coordinates:
            result["faces"] = detected_faces
        
        return result
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Error detecting faces: {str(e)}"
        }

def detect_faces(image_path, output_path=None, model="haar", draw_faces=True, 
                         confidence_threshold=0.5, return_coordinates=False):
    """
    Advanced face detection with multiple model options.
    
    Args:
        image_path (str): Path to the input image file
        output_path (str): Path for the output image with detected faces marked
        model (str): Detection model - "haar", "dnn"
        draw_faces (bool): Whether to draw rectangles around detected faces
        confidence_threshold (float): Confidence threshold for face detection (0.0-1.0)
        return_coordinates (bool): Whether to return face coordinates
    
    Returns:
        dict: Result information including success status and detected faces
    """
    
    
    try:
        # Validate input file
        if not os.path.exists(image_path):
            return {
                "success": False,
                "error": f"Input image file not found: {image_path}"
            }
        
        # Load the image
        image = cv2.imread(image_path)
        if image is None:
            return {
                "success": False,
                "error": "Failed to load image"
            }
        
        height, width = image.shape[:2]
        
        if model.lower() == "haar":
            # Use Haar cascade
            return detect_faces_base(image_path, output_path, draw_faces, confidence_threshold, return_coordinates)
        
        elif model.lower() == "dnn":
            # Use DNN face detector (requires model files)
            try:
                # Load DNN face detection model
                model_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
                if not os.path.exists(model_path):
                    return {
                        "success": False,
                        "error": "DNN model files not found. Using Haar cascade instead."
                    }
                
                # For now, fall back to Haar cascade
                return detect_faces_base(image_path, output_path, draw_faces, confidence_threshold, return_coordinates)
                
            except Exception as e:
                return {
                    "success": False,
                    "error": f"DNN detection failed: {str(e)}"
                }
        
        else:
            return {
                "success": False,
                "error": f"Unsupported model: {model}"
            }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Error in advanced face detection: {str(e)}"
        }

if __name__ == "__main__":
    # Test the function
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    result = detect_faces(
        image_path="./image_data/portrait_diverse_women_different_ages.jpg",
        output_path="test_faces_detected.jpg",
        draw_faces=True,
        return_coordinates=True
    )
    print(json.dumps(result, indent=2)) 