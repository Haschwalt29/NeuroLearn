import cv2
import numpy as np
from deepface import DeepFace
import time

class RealtimeEmotionDetector:
    def __init__(self):
        """Initialize real-time emotion detector"""
        print("Initializing Realtime Emotion Detector...")
        print("Press 'q' to quit, 's' to save current frame")
        
        # Initialize face cascade for faster face detection
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
        # Emotion colors for visualization
        self.emotion_colors = {
            'angry': (0, 0, 255),      # Red
            'disgust': (0, 255, 0),    # Green
            'fear': (255, 0, 255),     # Magenta
            'happy': (0, 255, 255),    # Yellow
            'sad': (255, 0, 0),        # Blue
            'surprise': (255, 255, 0), # Cyan
            'neutral': (128, 128, 128) # Gray
        }
        
        # Performance tracking
        self.frame_count = 0
        self.start_time = time.time()
        self.fps = 0
        
    def detect_faces_and_emotions(self, frame):
        """Detect faces and analyze emotions in real-time"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Detect faces using Haar Cascade (faster than DeepFace detection)
        faces = self.face_cascade.detectMultiScale(
            gray, 
            scaleFactor=1.1, 
            minNeighbors=5, 
            minSize=(30, 30)
        )
        
        # Process each detected face
        for (x, y, w, h) in faces:
            # Draw face rectangle
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
                
                # Get emotion data
                emotion = result[0]['dominant_emotion']
                confidence = result[0]['emotion'][emotion]
                
                # Get color for this emotion
                color = self.emotion_colors.get(emotion, (255, 255, 255))
                
                # Display emotion and confidence
                emotion_text = f"{emotion.upper()}: {confidence:.1f}%"
                cv2.putText(
                    frame, 
                    emotion_text,
                    (x, y-10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    color,
                    2
                )
                
                # Draw emotion bar
                bar_width = int(w * (confidence / 100))
                cv2.rectangle(
                    frame, 
                    (x, y+h+5), 
                    (x+bar_width, y+h+15), 
                    color, 
                    -1
                )
                
                # Show all emotions in a small text overlay
                emotions_text = ""
                for emo, conf in result[0]['emotion'].items():
                    if conf > 5:  # Only show emotions with >5% confidence
                        emotions_text += f"{emo}: {conf:.0f}% "
                
                if emotions_text:
                    cv2.putText(
                        frame,
                        emotions_text,
                        (x, y+h+25),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.4,
                        (255, 255, 255),
                        1
                    )
                
            except Exception as e:
                # If emotion detection fails, just show "Analyzing..."
                cv2.putText(
                    frame, 
                    "Analyzing...",
                    (x, y-10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 0, 255),
                    2
                )
        
        return frame
    
    def calculate_fps(self):
        """Calculate and display FPS"""
        self.frame_count += 1
        if self.frame_count % 30 == 0:  # Update FPS every 30 frames
            current_time = time.time()
            self.fps = 30 / (current_time - self.start_time)
            self.start_time = current_time
    
    def run(self, camera_index=0):
        """Run real-time emotion detection"""
        # Initialize camera
        cap = cv2.VideoCapture(camera_index)
        
        if not cap.isOpened():
            print(f"Error: Could not open camera {camera_index}")
            print("Try different camera indices: 0, 1, 2...")
            return
        
        # Set camera properties for better performance
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        cap.set(cv2.CAP_PROP_FPS, 30)
        
        print("Camera initialized successfully!")
        print("Starting real-time emotion detection...")
        
        frame_skip = 2  # Process every 2nd frame for better performance
        frame_counter = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Error: Could not read from camera")
                break
            
            # Skip frames for better performance
            frame_counter += 1
            if frame_counter % frame_skip != 0:
                continue
            
            # Calculate FPS
            self.calculate_fps()
            
            # Detect faces and emotions
            processed_frame = self.detect_faces_and_emotions(frame)
            
            # Add FPS counter
            cv2.putText(
                processed_frame,
                f"FPS: {self.fps:.1f}",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2
            )
            
            # Add instructions
            cv2.putText(
                processed_frame,
                "Press 'q' to quit, 's' to save",
                (10, processed_frame.shape[0] - 20),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 255, 255),
                1
            )
            
            # Display frame
            cv2.imshow('Real-time Emotion Detection', processed_frame)
            
            # Handle key presses
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s'):
                # Save current frame
                timestamp = int(time.time())
                filename = f'captured_emotion_{timestamp}.jpg'
                cv2.imwrite(filename, processed_frame)
                print(f"Frame saved as {filename}")
        
        # Cleanup
        cap.release()
        cv2.destroyAllWindows()
        print("Real-time detection stopped.")

def main():
    """Main function to run real-time emotion detection"""
    print("=" * 50)
    print("REAL-TIME EMOTION DETECTION")
    print("=" * 50)
    print("This will use your webcam for live emotion detection.")
    print("Make sure your camera is connected and not being used by other apps.")
    print()
    
    # Try different camera indices
    for camera_index in range(3):
        print(f"Trying camera index {camera_index}...")
        detector = RealtimeEmotionDetector()
        detector.run(camera_index)
        
        # Ask if user wants to try another camera
        if camera_index < 2:
            try_another = input("Camera not working? Try another index? (y/n): ").lower()
            if try_another != 'y':
                break

if __name__ == "__main__":
    main()
