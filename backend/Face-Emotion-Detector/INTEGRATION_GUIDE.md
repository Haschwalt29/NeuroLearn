# 🚀 Emotion Detection Integration Guide

This guide shows you how to integrate real-time emotion detection into your existing app with just a few lines of code!

## 📁 Files You Need

- `emotion-integration.js` - Core integration library
- `emotion-integration.css` - Styling (optional, customize as needed)
- Your backend running at `http://localhost:5000`

## 🎯 Quick Integration (3 Steps)

### 1. Add the Files to Your Project
```bash
# Copy these files to your project
cp emotion-integration.js /path/to/your/project/
cp emotion-integration.css /path/to/your/project/
```

### 2. Add HTML to Your Page
```html
<!-- Add this wherever you want emotion detection -->
<div id="emotionDetector"></div>

<!-- Include the files -->
<link rel="stylesheet" href="emotion-integration.css">
<script src="emotion-integration.js"></script>
```

### 3. Initialize in JavaScript
```javascript
// Simple integration
const detector = new EmotionDetectorIntegration({
  apiUrl: 'http://localhost:5000',  // Your backend URL
  onEmotionDetected: (data) => {
    console.log('Current emotion:', data.dominant_emotion);
    console.log('Confidence:', data.confidence);
    // Add your custom logic here
  }
});

// Start camera
const videoElement = document.getElementById('your-video-element');
await detector.startCamera(videoElement);
```

## 🎨 Framework-Specific Examples

### React
```jsx
import { EmotionDetectorIntegration } from './emotion-integration.js';
import './emotion-integration.css';

function MyComponent() {
  const [emotion, setEmotion] = useState(null);
  const detectorRef = useRef(null);
  const videoRef = useRef(null);

  useEffect(() => {
    detectorRef.current = new EmotionDetectorIntegration({
      onEmotionDetected: (data) => setEmotion(data.dominant_emotion)
    });
  }, []);

  const startCamera = () => {
    detectorRef.current?.startCamera(videoRef.current);
  };

  return (
    <div>
      <video ref={videoRef} autoPlay muted />
      <button onClick={startCamera}>Start Detection</button>
      {emotion && <p>Current emotion: {emotion}</p>}
    </div>
  );
}
```

### Vue.js
```vue
<template>
  <div>
    <video ref="videoElement" autoplay muted />
    <button @click="startCamera">Start Detection</button>
    <p v-if="emotion">Current emotion: {{ emotion }}</p>
  </div>
</template>

<script>
import { EmotionDetectorIntegration } from './emotion-integration.js';

export default {
  data() {
    return {
      emotion: null,
      detector: null
    };
  },
  mounted() {
    this.detector = new EmotionDetectorIntegration({
      onEmotionDetected: (data) => this.emotion = data.dominant_emotion
    });
  },
  methods: {
    async startCamera() {
      await this.detector.startCamera(this.$refs.videoElement);
    }
  }
};
</script>
```

### Angular
```typescript
import { Component, ElementRef, ViewChild } from '@angular/core';

@Component({
  selector: 'app-emotion-detector',
  template: `
    <video #videoElement autoplay muted></video>
    <button (click)="startCamera()">Start Detection</button>
    <p *ngIf="emotion">Current emotion: {{ emotion }}</p>
  `
})
export class EmotionDetectorComponent {
  @ViewChild('videoElement') videoElement!: ElementRef;
  
  emotion: string | null = null;
  private detector: any;

  ngOnInit() {
    // Import the EmotionDetectorIntegration
    this.detector = new (window as any).EmotionDetectorIntegration({
      onEmotionDetected: (data: any) => this.emotion = data.dominant_emotion
    });
  }

  async startCamera() {
    await this.detector.startCamera(this.videoElement.nativeElement);
  }
}
```

## ⚙️ Configuration Options

```javascript
const detector = new EmotionDetectorIntegration({
  apiUrl: 'http://localhost:5000',        // Backend URL
  detectionInterval: 1000,                // Analysis frequency (ms)
  onEmotionDetected: (data) => {          // Callback when emotion detected
    console.log('Emotion:', data.dominant_emotion);
    console.log('All emotions:', data.emotions);
  },
  onError: (error) => {                   // Error callback
    console.error('Detection error:', error);
  }
});
```

## 🎨 Customization

### Custom Styling
```css
/* Override default styles */
.emotion-overlay {
  background: rgba(255, 0, 0, 0.8);  /* Red background */
  color: white;
  font-size: 24px;                   /* Larger text */
}

.emotion-btn-start {
  background: linear-gradient(45deg, #ff6b6b, #ee5a24);
  border-radius: 50px;               /* Rounder buttons */
}
```

### Custom Emotion Colors
```javascript
const detector = new EmotionDetectorIntegration({
  onEmotionDetected: (data) => {
    const colors = {
      happy: '#00ff00',
      sad: '#0000ff',
      angry: '#ff0000'
    };
    
    const color = colors[data.dominant_emotion] || '#ffffff';
    document.body.style.backgroundColor = color;
  }
});
```

## 🔧 API Reference

### Methods
- `startCamera(videoElement)` - Start camera and detection
- `stopCamera()` - Stop camera and detection
- `getCurrentEmotion()` - Get current emotion data
- `destroy()` - Clean up resources

### Data Structure
```javascript
{
  dominant_emotion: 'happy',
  confidence: 85.2,
  emotions: {
    happy: 85.2,
    neutral: 10.1,
    sad: 2.3,
    angry: 1.2,
    fear: 0.8,
    surprise: 0.4,
    disgust: 0.0
  }
}
```

## 🚀 Backend Setup

Make sure your Flask backend is running:

```bash
# Start the backend
python web_app.py

# Backend will be available at http://localhost:5000
```

## 📱 Mobile Support

The integration works on mobile devices! Just make sure to:

1. Use HTTPS in production (required for camera access)
2. Handle orientation changes
3. Test on different screen sizes

## 🐛 Troubleshooting

### Camera Not Working
- Check browser permissions
- Try different camera indices
- Ensure HTTPS in production

### API Errors
- Verify backend is running
- Check CORS settings
- Update API URL if needed

### Performance Issues
- Increase `detectionInterval` (e.g., 2000ms)
- Reduce video resolution
- Close other camera-using apps

## 💡 Tips

1. **Start Simple**: Begin with basic integration, then add features
2. **Handle Errors**: Always implement error callbacks
3. **Test Thoroughly**: Try different lighting conditions
4. **Customize UI**: Match your app's design system
5. **Monitor Performance**: Watch FPS and adjust settings

## 🎉 You're Ready!

That's it! You now have real-time emotion detection integrated into your app. The emotion detection will work with 88%+ accuracy using the pretrained DeepFace model.

Need help? Check the examples in the `integration-examples/` folder or customize the code to fit your needs!
