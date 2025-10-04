/**
 * Universal Emotion Detection Integration
 * Works with any frontend framework or vanilla JS
 */

class EmotionDetectorIntegration {
  constructor(options = {}) {
    this.options = {
      apiUrl: options.apiUrl || 'http://localhost:5000',
      detectionInterval: options.detectionInterval || 1000,
      onEmotionDetected: options.onEmotionDetected || null,
      onError: options.onError || null,
      ...options
    };

    this.isActive = false;
    this.currentEmotion = null;
    this.emotions = {};
    this.stream = null;
    this.intervalId = null;
    this.frameCount = 0;
    this.lastTime = Date.now();
    this.fps = 0;

    this.emotionColors = {
      angry: '#ff4444',
      disgust: '#44ff44',
      fear: '#ff44ff',
      happy: '#ffff44',
      sad: '#4444ff',
      surprise: '#44ffff',
      neutral: '#888888'
    };
  }

  async startCamera(videoElement) {
    try {
      this.videoElement = videoElement;
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { width: 640, height: 480 }
      });
      
      this.stream = stream;
      this.videoElement.srcObject = stream;
      this.isActive = true;
      
      this.startEmotionDetection();
      return true;
    } catch (err) {
      this.options.onError?.(err);
      return false;
    }
  }

  stopCamera() {
    if (this.stream) {
      this.stream.getTracks().forEach(track => track.stop());
      this.stream = null;
    }
    if (this.videoElement) {
      this.videoElement.srcObject = null;
    }
    if (this.intervalId) {
      clearInterval(this.intervalId);
      this.intervalId = null;
    }
    
    this.isActive = false;
    this.currentEmotion = null;
    this.emotions = {};
  }

  startEmotionDetection() {
    if (this.intervalId) return;
    
    this.intervalId = setInterval(async () => {
      if (!this.isActive || !this.videoElement) return;
      
      // Calculate FPS
      this.frameCount++;
      const now = Date.now();
      if (now - this.lastTime >= 1000) {
        this.fps = Math.round((this.frameCount * 1000) / (now - this.lastTime));
        this.frameCount = 0;
        this.lastTime = now;
      }
      
      // Capture and analyze frame
      await this.captureAndAnalyze();
    }, this.options.detectionInterval);
  }

  async captureAndAnalyze() {
    if (!this.videoElement) return;
    
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    canvas.width = this.videoElement.videoWidth;
    canvas.height = this.videoElement.videoHeight;
    ctx.drawImage(this.videoElement, 0, 0);
    
    const blob = await new Promise(resolve => {
      canvas.toBlob(resolve, 'image/jpeg', 0.8);
    });
    
    if (blob) {
      await this.analyzeEmotion(blob);
    }
  }

  async analyzeEmotion(blob) {
    try {
      const formData = new FormData();
      formData.append('file', blob);

      const response = await fetch(`${this.options.apiUrl}/upload`, {
        method: 'POST',
        body: formData
      });

      const data = await response.json();
      
      if (data.success) {
        this.currentEmotion = data.dominant_emotion;
        this.emotions = data.emotions;
        this.options.onEmotionDetected?.(data);
      } else {
        this.currentEmotion = null;
        this.emotions = {};
      }
    } catch (err) {
      this.options.onError?.(err);
    }
  }

  getCurrentEmotion() {
    return {
      emotion: this.currentEmotion,
      emotions: this.emotions,
      fps: this.fps,
      isActive: this.isActive
    };
  }

  destroy() {
    this.stopCamera();
  }
}

// Export for different module systems
if (typeof module !== 'undefined' && module.exports) {
  module.exports = EmotionDetectorIntegration;
} else if (typeof define === 'function' && define.amd) {
  define([], () => EmotionDetectorIntegration);
} else {
  window.EmotionDetectorIntegration = EmotionDetectorIntegration;
}
