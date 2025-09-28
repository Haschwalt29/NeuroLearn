// React Integration Example
import React, { useState, useRef, useEffect } from 'react';
import { EmotionDetectorIntegration } from '../emotion-integration.js';
import '../emotion-integration.css';

const EmotionDetectorComponent = ({ onEmotionDetected, className = '' }) => {
  const [isActive, setIsActive] = useState(false);
  const [currentEmotion, setCurrentEmotion] = useState(null);
  const [emotions, setEmotions] = useState({});
  const [fps, setFps] = useState(0);
  const [error, setError] = useState(null);
  
  const videoRef = useRef(null);
  const detectorRef = useRef(null);

  useEffect(() => {
    // Initialize detector
    detectorRef.current = new EmotionDetectorIntegration({
      apiUrl: 'http://localhost:5000',
      detectionInterval: 1000,
      onEmotionDetected: (data) => {
        setCurrentEmotion(data.dominant_emotion);
        setEmotions(data.emotions);
        onEmotionDetected?.(data);
      },
      onError: (err) => {
        setError(err.message);
      }
    });

    return () => {
      detectorRef.current?.destroy();
    };
  }, [onEmotionDetected]);

  const startCamera = async () => {
    const success = await detectorRef.current?.startCamera(videoRef.current);
    if (success) {
      setIsActive(true);
      setError(null);
    }
  };

  const stopCamera = () => {
    detectorRef.current?.stopCamera();
    setIsActive(false);
    setCurrentEmotion(null);
    setEmotions({});
  };

  const getEmotionColor = (emotion) => {
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
  };

  return (
    <div className={`emotion-detector-container ${className}`}>
      <div className="emotion-detector-container">
        <video
          ref={videoRef}
          autoPlay
          muted
          playsInline
          className="emotion-video"
        />
        {currentEmotion && (
          <div 
            className="emotion-overlay"
            style={{ 
              color: getEmotionColor(currentEmotion),
              borderColor: getEmotionColor(currentEmotion)
            }}
          >
            {currentEmotion.toUpperCase()}
          </div>
        )}
      </div>

      <div className="emotion-controls">
        <button
          onClick={isActive ? stopCamera : startCamera}
          className={`emotion-btn ${isActive ? 'emotion-btn-stop' : 'emotion-btn-start'}`}
        >
          {isActive ? 'Stop Camera' : 'Start Camera'}
        </button>
      </div>

      <div className="emotion-stats">
        <div className="emotion-stat">
          <span className="emotion-stat-value">{fps}</span>
          <span className="emotion-stat-label">FPS</span>
        </div>
        <div className="emotion-stat">
          <span className="emotion-stat-value">
            {currentEmotion ? currentEmotion.toUpperCase() : '-'}
          </span>
          <span className="emotion-stat-label">Emotion</span>
        </div>
      </div>

      {currentEmotion && (
        <div className="emotion-bars">
          <h4>Emotion Analysis</h4>
          {Object.entries(emotions).map(([emotion, confidence]) => (
            <div key={emotion} className="emotion-bar">
              <div className="emotion-bar-label">
                {emotion.charAt(0).toUpperCase() + emotion.slice(1)}
              </div>
              <div className="emotion-bar-container">
                <div
                  className="emotion-bar-fill"
                  style={{
                    width: `${confidence}%`,
                    backgroundColor: getEmotionColor(emotion)
                  }}
                />
              </div>
              <div className="emotion-bar-value">{confidence.toFixed(1)}%</div>
            </div>
          ))}
        </div>
      )}

      {error && (
        <div className="emotion-error">
          {error}
        </div>
      )}
    </div>
  );
};

export default EmotionDetectorComponent;
