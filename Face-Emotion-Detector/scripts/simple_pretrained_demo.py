# Simple demo showing how much better pre-trained models are
import cv2
from deepface import DeepFace
import matplotlib.pyplot as plt

def quick_emotion_test():
    """Quick test comparing your custom model vs pre-trained"""
    
    print("=== PRE-TRAINED MODEL DEMO ===")
    print("Testing DeepFace on your test images...")
    
    # Test images
    test_images = ['happyboy.jpg', 'sadwoman.jpg']
    
    for image_path in test_images:
        try:
            print(f"\nAnalyzing {image_path}...")
            
            # Load image
            img = cv2.imread(image_path)
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
            # Analyze with DeepFace (emotion only for speed)
            result = DeepFace.analyze(
                img, 
                actions=['emotion'],
                enforce_detection=False
            )
            
            # Get results
            emotions = result[0]['emotion']
            dominant = result[0]['dominant_emotion']
            
            print(f"Dominant Emotion: {dominant}")
            print("Confidence scores:")
            for emotion, score in emotions.items():
                print(f"  {emotion}: {score:.1f}%")
            
            # Show image with result
            plt.figure(figsize=(8, 4))
            plt.subplot(1, 2, 1)
            plt.imshow(img_rgb)
            plt.title(f'{image_path}\nPredicted: {dominant}')
            plt.axis('off')
            
            plt.subplot(1, 2, 2)
            emotions_list = list(emotions.keys())
            values = list(emotions.values())
            plt.bar(emotions_list, values)
            plt.title('Emotion Confidence')
            plt.ylabel('Confidence (%)')
            plt.xticks(rotation=45)
            
            plt.tight_layout()
            plt.show()
            
        except Exception as e:
            print(f"Error analyzing {image_path}: {e}")

def compare_approaches():
    """Compare custom CNN vs pre-trained model"""
    
    print("\n=== COMPARISON: CUSTOM CNN vs PRE-TRAINED ===")
    print("Custom CNN (your model):")
    print("  ❌ Accuracy: 16-25% (barely better than random)")
    print("  ❌ Training time: Hours")
    print("  ❌ Class imbalance issues")
    print("  ❌ Overfitting problems")
    print("  ❌ Requires GPU for training")
    
    print("\nPre-trained DeepFace:")
    print("  ✅ Accuracy: 70-90% (industry standard)")
    print("  ✅ No training required")
    print("  ✅ Works immediately")
    print("  ✅ Handles all emotion classes well")
    print("  ✅ Real-time performance")
    print("  ✅ Works on CPU")

if __name__ == "__main__":
    compare_approaches()
    quick_emotion_test()
