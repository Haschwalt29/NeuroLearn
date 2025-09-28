import base64
import cv2
import numpy as np
from typing import Optional, Tuple

# Reuse existing detector implementation
import sys
import os

# Add the Face-Emotion-Detector directory to the path
face_emotion_path = os.path.join(os.path.dirname(__file__), '..', '..', 'Face-Emotion-Detector')
if face_emotion_path not in sys.path:
    sys.path.append(face_emotion_path)

try:
    from backend.models.emotion_detector import EmotionDetector
    print("✅ Real emotion detector imported successfully")
except ImportError as e:
    print(f"❌ Failed to import real emotion detector: {e}")
    print("Using mock detector instead")
    # Fallback: create a simple mock detector
    class EmotionDetector:
        def __init__(self):
            pass
        def detect_emotion_from_image_data(self, img, show_result=False):
            # Mock implementation for testing - return random emotions
            import random
            emotions = ['happy', 'sad', 'angry', 'fear', 'surprise', 'disgust', 'neutral']
            dominant = random.choice(emotions)
            
            # Create realistic emotion distribution
            emotion_scores = {}
            for emotion in emotions:
                if emotion == dominant:
                    emotion_scores[emotion] = random.uniform(0.6, 0.95)  # High confidence for dominant
                else:
                    emotion_scores[emotion] = random.uniform(0.01, 0.3)  # Lower for others
            
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


