<!-- Vue.js Integration Example -->
<template>
  <div class="emotion-detector-container">
    <div class="emotion-detector-container">
      <video
        ref="videoElement"
        autoplay
        muted
        playsinline
        class="emotion-video"
      />
      <div 
        v-if="currentEmotion"
        class="emotion-overlay"
        :style="{ 
          color: getEmotionColor(currentEmotion),
          borderColor: getEmotionColor(currentEmotion)
        }"
      >
        {{ currentEmotion.toUpperCase() }}
      </div>
    </div>

    <div class="emotion-controls">
      <button
        @click="isActive ? stopCamera() : startCamera()"
        :class="['emotion-btn', isActive ? 'emotion-btn-stop' : 'emotion-btn-start']"
      >
        {{ isActive ? 'Stop Camera' : 'Start Camera' }}
      </button>
    </div>

    <div class="emotion-stats">
      <div class="emotion-stat">
        <span class="emotion-stat-value">{{ fps }}</span>
        <span class="emotion-stat-label">FPS</span>
      </div>
      <div class="emotion-stat">
        <span class="emotion-stat-value">
          {{ currentEmotion ? currentEmotion.toUpperCase() : '-' }}
        </span>
        <span class="emotion-stat-label">Emotion</span>
      </div>
    </div>

    <div v-if="currentEmotion" class="emotion-bars">
      <h4>Emotion Analysis</h4>
      <div 
        v-for="(confidence, emotion) in emotions" 
        :key="emotion"
        class="emotion-bar"
      >
        <div class="emotion-bar-label">
          {{ emotion.charAt(0).toUpperCase() + emotion.slice(1) }}
        </div>
        <div class="emotion-bar-container">
          <div
            class="emotion-bar-fill"
            :style="{
              width: `${confidence}%`,
              backgroundColor: getEmotionColor(emotion)
            }"
          />
        </div>
        <div class="emotion-bar-value">{{ confidence.toFixed(1) }}%</div>
      </div>
    </div>

    <div v-if="error" class="emotion-error">
      {{ error }}
    </div>
  </div>
</template>

<script>
import { EmotionDetectorIntegration } from '../emotion-integration.js';
import '../emotion-integration.css';

export default {
  name: 'EmotionDetector',
  props: {
    onEmotionDetected: {
      type: Function,
      default: null
    }
  },
  data() {
    return {
      isActive: false,
      currentEmotion: null,
      emotions: {},
      fps: 0,
      error: null,
      detector: null
    };
  },
  mounted() {
    this.detector = new EmotionDetectorIntegration({
      apiUrl: 'http://localhost:5000',
      detectionInterval: 1000,
      onEmotionDetected: (data) => {
        this.currentEmotion = data.dominant_emotion;
        this.emotions = data.emotions;
        this.onEmotionDetected?.(data);
      },
      onError: (err) => {
        this.error = err.message;
      }
    });
  },
  beforeUnmount() {
    this.detector?.destroy();
  },
  methods: {
    async startCamera() {
      const success = await this.detector?.startCamera(this.$refs.videoElement);
      if (success) {
        this.isActive = true;
        this.error = null;
      }
    },
    stopCamera() {
      this.detector?.stopCamera();
      this.isActive = false;
      this.currentEmotion = null;
      this.emotions = {};
    },
    getEmotionColor(emotion) {
      const colors = {
        angry: '#ff4444',
        disgust: '#44ff44',
        fear: '#ff44ff',
        happy: '#ffff44',
        sad: '#4444ff',
        surprise: '#44ffff',
        neutral: '#888888'
      };
      return colors[emotion] || '#ffffff';
    }
  }
};
</script>
