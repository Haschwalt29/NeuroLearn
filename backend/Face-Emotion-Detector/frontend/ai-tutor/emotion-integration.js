/**
 * Universal Emotion Detection Integration
 * Optimized for AI Tutor Application
 */

class EmotionDetectorIntegration {
  constructor(options = {}) {
    this.options = {
      apiUrl: options.apiUrl || 'http://localhost:5000',
      detectionInterval: options.detectionInterval || 2000,
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
    this.retryCount = 0;
    this.maxRetries = 3;

    this.emotionColors = {
      angry: '#ef4444',
      disgust: '#84cc16',
      fear: '#8b5cf6',
      happy: '#10b981',
      sad: '#3b82f6',
      surprise: '#f59e0b',
      neutral: '#6b7280'
    };
  }

  async startCamera(videoElement) {
    try {
      this.videoElement = videoElement;
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { 
          width: { ideal: 640 },
          height: { ideal: 480 },
          facingMode: 'user'
        }
      });
      
      this.stream = stream;
      this.videoElement.srcObject = stream;
      this.isActive = true;
      this.retryCount = 0;
      
      // Wait for video to be ready
      await this.waitForVideoReady();
      this.startEmotionDetection();
      
      return true;
    } catch (err) {
      console.error('Camera access error:', err);
      this.options.onError?.(err);
      return false;
    }
  }

  waitForVideoReady() {
    return new Promise((resolve) => {
      if (this.videoElement.readyState >= 2) {
        resolve();
      } else {
        this.videoElement.addEventListener('loadedmetadata', resolve, { once: true });
      }
    });
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
    if (!this.videoElement || this.videoElement.readyState < 2) return;
    
    try {
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
    } catch (error) {
      console.error('Frame capture error:', error);
    }
  }

  async analyzeEmotion(blob) {
    try {
      const formData = new FormData();
      formData.append('file', blob);

      console.log('Sending request to:', `${this.options.apiUrl}/upload`); // Debug log

      const response = await fetch(`${this.options.apiUrl}/upload`, {
        method: 'POST',
        body: formData,
        mode: 'cors' // Explicitly set CORS mode
      });

      console.log('Response status:', response.status); // Debug log

      if (!response.ok) {
        const errorText = await response.text();
        console.error('Server error response:', errorText);
        throw new Error(`HTTP error! status: ${response.status}, message: ${errorText}`);
      }

      const data = await response.json();
      console.log('Response data:', data); // Debug log
      
      if (data.success) {
        this.currentEmotion = data.dominant_emotion;
        this.emotions = data.emotions;
        this.retryCount = 0; // Reset retry count on success
        this.options.onEmotionDetected?.(data);
      } else {
        this.currentEmotion = null;
        this.emotions = {};
        this.handleAnalysisError(data.error || 'Analysis failed');
      }
    } catch (err) {
      console.error('Emotion analysis error:', err);
      this.handleAnalysisError(err.message);
    }
  }

  handleAnalysisError(error) {
    this.retryCount++;
    
    if (this.retryCount >= this.maxRetries) {
      this.options.onError?.(new Error(`Analysis failed after ${this.maxRetries} retries: ${error}`));
      this.retryCount = 0; // Reset for next attempt
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

  getEmotionColor(emotion) {
    return this.emotionColors[emotion] || '#6b7280';
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
