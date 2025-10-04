import cv2
import numpy as np
import matplotlib.pyplot as plt
from deepface import DeepFace
import os
from pathlib import Path

class EmotionDetector:
    def __init__(self, model_name='emotion'):
        """
        Initialize emotion detector with DeepFace
        
        Available models: 'emotion', 'age', 'gender', 'race', 'deepface'
        """
        self.model_name = model_name
        print(f"Initialized DeepFace with {model_name} model")
    
    def detect_emotion_from_image(self, image_path, show_result=True):
        """
        Detect emotion from a single image
        
        Args:
            image_path (str): Path to image file
            show_result (bool): Whether to display the result
        
        Returns:
            dict: Emotion analysis results
        """
        try:
            # Load image
            img = cv2.imread(image_path)
            if img is None:
                raise ValueError(f"Could not load image: {image_path}")
            
            return self.detect_emotion_from_image_data(img, show_result, image_path)
            
        except Exception as e:
            print(f"Error analyzing {image_path}: {e}")
            return None
    
    def detect_emotion_from_image_data(self, img, show_result=True, image_path=None):
        """
        Detect emotion from image data (numpy array)
        
        Args:
            img (numpy.ndarray): Image data as numpy array
            show_result (bool): Whether to display the result
            image_path (str): Optional image path for display
        
        Returns:
            dict: Emotion analysis results
        """
        try:
            # Analyze emotion only (faster than full analysis)
            result = DeepFace.analyze(
                img, 
                actions=['emotion'],  # Only emotion, not race/age/gender
                enforce_detection=False,  # Don't fail if no face detected
                detector_backend='opencv'  # Use OpenCV for face detection
            )
            
            if show_result and image_path:
                self._display_result(img, result, image_path)
            
            return result
            
        except Exception as e:
            print(f"Error analyzing image: {e}")
            return None
    
    def detect_emotion_from_webcam(self, camera_index=0):
        """
        Real-time emotion detection from webcam
        
        Args:
            camera_index (int): Camera index (0 for default camera)
        """
        # Initialize face cascade
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
        # Initialize camera
        cap = cv2.VideoCapture(camera_index)
        if not cap.isOpened():
            print(f"Error: Could not open camera {camera_index}")
            return
        
        print("Press 'q' to quit, 's' to save current frame")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Error: Could not read from camera")
                break
            
            # Detect faces
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)
            
            # Process each face
            for (x, y, w, h) in faces:
                # Draw rectangle around face
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                
                # Extract face region
                face_roi = frame[y:y+h, x:x+w]
                
                try:
                    # Analyze emotion for this face
                    result = DeepFace.analyze(
                        face_roi,
                        actions=['emotion'],
                        enforce_detection=False,
                        detector_backend='opencv'
                    )
                    
                    # Get dominant emotion
                    emotion = result[0]['dominant_emotion']
                    confidence = result[0]['emotion'][emotion]
                    
                    # Display emotion on frame
                    cv2.putText(
                        frame, 
                        f"{emotion}: {confidence:.1f}%",
                        (x, y-10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        (0, 255, 0),
                        2
                    )
                    
                except Exception as e:
                    cv2.putText(
                        frame, 
                        "No emotion detected",
                        (x, y-10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        (0, 0, 255),
                        2
                    )
            
            # Display frame
            cv2.imshow('Emotion Detection', frame)
            
            # Handle key presses
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s'):
                # Save current frame
                cv2.imwrite('captured_emotion.jpg', frame)
                print("Frame saved as 'captured_emotion.jpg'")
        
        # Cleanup
        cap.release()
        cv2.destroyAllWindows()
    
    def batch_emotion_detection(self, image_dir, output_file='emotion_results.csv'):
        """
        Detect emotions for all images in a directory
        
        Args:
            image_dir (str): Directory containing images
            output_file (str): Output CSV file for results
        """
        import pandas as pd
        
        results = []
        image_files = []
        
        # Get all image files
        for ext in ['*.jpg', '*.jpeg', '*.png', '*.bmp']:
            image_files.extend(Path(image_dir).glob(ext))
        
        print(f"Found {len(image_files)} images to process")
        
        for i, image_path in enumerate(image_files):
            print(f"Processing {i+1}/{len(image_files)}: {image_path.name}")
            
            result = self.detect_emotion_from_image(str(image_path), show_result=False)
            
            if result:
                emotion_data = result[0]['emotion']
                emotion_data['image'] = image_path.name
                emotion_data['dominant_emotion'] = result[0]['dominant_emotion']
                results.append(emotion_data)
            else:
                # Add row with no emotion detected
                no_emotion = {
                    'image': image_path.name,
                    'dominant_emotion': 'no_emotion',
                    'angry': 0, 'disgust': 0, 'fear': 0, 'happy': 0,
                    'sad': 0, 'surprise': 0, 'neutral': 0
                }
                results.append(no_emotion)
        
        # Save results
        df = pd.DataFrame(results)
        df.to_csv(output_file, index=False)
        print(f"Results saved to {output_file}")
        
        # Print summary
        print("\nEmotion Distribution:")
        print(df['dominant_emotion'].value_counts())
        
        return df
    
    def _display_result(self, img, result, image_path):
        """Display the emotion detection result"""
        # Convert BGR to RGB for matplotlib
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # Get emotion data
        emotions = result[0]['emotion']
        dominant_emotion = result[0]['dominant_emotion']
        
        # Create subplot
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        
        # Show image
        ax1.imshow(img_rgb)
        ax1.set_title(f'Image: {os.path.basename(image_path)}')
        ax1.axis('off')
        
        # Show emotion bar chart
        emotions_list = list(emotions.keys())
        values = list(emotions.values())
        colors = ['red' if e == dominant_emotion else 'lightblue' for e in emotions_list]
        
        bars = ax2.bar(emotions_list, values, color=colors)
        ax2.set_title(f'Emotion Analysis\nDominant: {dominant_emotion}')
        ax2.set_ylabel('Confidence (%)')
        ax2.tick_params(axis='x', rotation=45)
        
        # Add value labels on bars
        for bar, value in zip(bars, values):
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                    f'{value:.1f}%', ha='center', va='bottom')
        
        plt.tight_layout()
        plt.show()
        
        # Print detailed results
        print(f"\nEmotion Analysis for {os.path.basename(image_path)}:")
        print(f"Dominant Emotion: {dominant_emotion}")
        print("All Emotions:")
        for emotion, confidence in emotions.items():
            print(f"  {emotion}: {confidence:.2f}%")

# Example usage
if __name__ == "__main__":
    # Initialize detector
    detector = EmotionDetector()
    
    # Test with your existing images
    print("Testing with happyboy.jpg...")
    detector.detect_emotion_from_image('happyboy.jpg')
    
    print("\nTesting with sadwoman.jpg...")
    detector.detect_emotion_from_image('sadwoman.jpg')
    
    # Uncomment to test webcam
    # print("\nStarting webcam detection...")
    # detector.detect_emotion_from_webcam()
    
    # Uncomment to test batch processing
    # print("\nProcessing test images...")
    # detector.batch_emotion_detection('images/test/happy', 'happy_emotions.csv')
