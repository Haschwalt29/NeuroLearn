from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
import cv2
import numpy as np
import base64
from models.emotion_detector import EmotionDetector
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
detector = EmotionDetector()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/detect_emotion', methods=['POST'])
def detect_emotion():
    try:
        # Get image data from request
        data = request.get_json()
        image_data = data['image']
        
        # Remove data URL prefix
        if ',' in image_data:
            image_data = image_data.split(',')[1]
        
        # Decode base64 image
        image_bytes = base64.b64decode(image_data)
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            return jsonify({'error': 'Could not decode image'}), 400
        
        # Analyze emotion
        result = detector.detect_emotion_from_image_data(img, show_result=False)
        
        if result:
            emotions = result[0]['emotion']
            dominant_emotion = result[0]['dominant_emotion']
            
            # Convert numpy types to native Python types for JSON serialization
            emotions_serializable = {k: float(v) for k, v in emotions.items()}
            confidence_value = float(emotions[dominant_emotion]) if dominant_emotion in emotions else None
            
            return jsonify({
                'success': True,
                'dominant_emotion': dominant_emotion,
                'emotions': emotions_serializable,
                'confidence': confidence_value
            })
        else:
            return jsonify({'error': 'No emotion detected'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/realtime')
def realtime():
    """Route for real-time detection page"""
    return render_template('realtime.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        print("Upload request received")  # Debug log
        
        if 'file' not in request.files:
            print("No file in request")  # Debug log
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            print("Empty filename")  # Debug log
            return jsonify({'error': 'No file selected'}), 400
        
        print(f"Processing file: {file.filename}")  # Debug log
        
        # Read image
        img_bytes = file.read()
        nparr = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            print("Could not decode image")  # Debug log
            return jsonify({'error': 'Could not decode image'}), 400
        
        print(f"Image decoded successfully, shape: {img.shape}")  # Debug log
        
        # Analyze emotion
        result = detector.detect_emotion_from_image_data(img, show_result=False)
        
        if result:
            emotions = result[0]['emotion']
            dominant_emotion = result[0]['dominant_emotion']
            
            print(f"Emotion detected: {dominant_emotion}")  # Debug log
            
            # Convert numpy types to native Python types for JSON serialization
            emotions_serializable = {k: float(v) for k, v in emotions.items()}
            confidence_value = float(emotions[dominant_emotion]) if dominant_emotion in emotions else None
            
            return jsonify({
                'success': True,
                'dominant_emotion': dominant_emotion,
                'emotions': emotions_serializable,
                'confidence': confidence_value
            })
        else:
            print("No emotion detected")  # Debug log
            return jsonify({'error': 'No emotion detected'}), 400
            
    except Exception as e:
        print(f"Error in upload: {str(e)}")  # Debug log
        import traceback
        traceback.print_exc()  # Print full traceback
        return jsonify({'error': f'Server error: {str(e)}'}), 500

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    app.run(debug=True, host='0.0.0.0', port=5000)
