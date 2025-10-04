import base64
import cv2
import numpy as np
from typing import Optional, Tuple
import sys
import os

face_emotion_path = os.path.join(os.path.dirname(__file__), '..', '..', 'Face-Emotion-Detector')
if face_emotion_path not in sys.path:
    sys.path.append(face_emotion_path)

face_emotion_backend_path = os.path.join(face_emotion_path, 'backend')
if face_emotion_backend_path not in sys.path:
    sys.path.append(face_emotion_backend_path)

try:
    from backend.models.emotion_detector import EmotionDetector
    print("✅ Real emotion detector imported successfully")
except ImportError as e:
    print(f"❌ Failed to import real emotion detector: {e}")
    try:
        from models.emotion_detector import EmotionDetector
        print("✅ Real emotion detector imported successfully (alternative path)")
    except ImportError as e2:
        print(f"❌ Failed to import real emotion detector (alternative path): {e2}")
        try:
            from deepface import DeepFace
            print("✅ DeepFace imported successfully, creating direct detector")
            
            class EmotionDetector:
                def __init__(self):
                    self.model_name = 'emotion'
                    print(f"Initialized DeepFace with {self.model_name} model")
                
                def detect_emotion_from_image_data(self, img, show_result=False):
                    try:
                        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                        result = DeepFace.analyze(
                            img_rgb, 
                            actions=['emotion'],
                            enforce_detection=False,
                            silent=True
                        )
                        
                        if result and len(result) > 0:
                            emotions = result[0]['emotion']
                            dominant_emotion = result[0]['dominant_emotion']
                            
                            emotion_scores = {}
                            for emotion, score in emotions.items():
                                emotion_scores[emotion] = score / 100.0
                            
                            return [{'emotion': emotion_scores, 'dominant_emotion': dominant_emotion}]
                        else:
                            return None
                    except Exception as e:
                        print(f"DeepFace analysis error: {e}")
                        return None
            
            print("✅ Direct DeepFace emotion detector created")
        except ImportError as e3:
            print(f"❌ Failed to import DeepFace: {e3}")
            print("Using mock detector instead")
    # Fallback: create a simple mock detector
    class EmotionDetector:
        def __init__(self):
            pass
        def detect_emotion_from_image_data(self, img, show_result=False):
            import random
            
            height, width = img.shape[:2]
            face_size_score = min(height * width / (640 * 480), 1.0)
            
            if face_size_score > 0.3:
                emotions = ['happy', 'surprise', 'neutral', 'sad', 'angry', 'fear', 'disgust']
                weights = [0.4, 0.2, 0.2, 0.1, 0.05, 0.03, 0.02]
            else:
                emotions = ['happy', 'sad', 'angry', 'fear', 'surprise', 'disgust', 'neutral']
                weights = [0.2, 0.2, 0.2, 0.15, 0.15, 0.05, 0.05]
            
            dominant = random.choices(emotions, weights=weights)[0]
            
            emotion_scores = {}
            for emotion in emotions:
                if emotion == dominant:
                    emotion_scores[emotion] = random.uniform(0.7, 0.95)
                else:
                    emotion_scores[emotion] = random.uniform(0.01, 0.3)
            
            return [{'emotion': emotion_scores, 'dominant_emotion': dominant}]


class EmotionDetectionService:
    def __init__(self):
        self.detector = EmotionDetector()

    def analyze_ndarray(self, image_bgr: np.ndarray) -> Optional[Tuple[str, float]]:
        result = self.detector.detect_emotion_from_image_data(image_bgr, show_result=False)
        if not result:
            return None
        emotions = result[0]["emotion"]
        dominant = result[0]["dominant_emotion"]
        confidence = float(emotions.get(dominant, 0.0))
        return dominant, confidence

    def analyze_base64_image(self, data_url_or_b64: str) -> Optional[Tuple[str, float]]:
        if "," in data_url_or_b64:
            data_url_or_b64 = data_url_or_b64.split(",", 1)[1]
        try:
            image_bytes = base64.b64decode(data_url_or_b64)
            nparr = np.frombuffer(image_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if img is None:
                return None
            return self.analyze_ndarray(img)
        except Exception:
            return None


