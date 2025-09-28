import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Camera, CameraOff, Eye, Smile, Frown, Meh, AlertTriangle, Heart } from 'lucide-react';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'https://neurolearn-6c0k.onrender.com';

const LiveEmotionDetector = ({ onEmotionDetected, isEnabled = true }) => {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const [isStreaming, setIsStreaming] = useState(false);
  const [currentEmotion, setCurrentEmotion] = useState(null);
  const [confidence, setConfidence] = useState(0);
  const [error, setError] = useState(null);
  const [isDetecting, setIsDetecting] = useState(false);
  const [emotionHistory, setEmotionHistory] = useState([]);
  const [showHistory, setShowHistory] = useState(false);
  const streamRef = useRef(null);
  const detectionIntervalRef = useRef(null);
  const resultsBufferRef = useRef([]); // rolling window of recent results
  const lastUpdateRef = useRef(0); // timestamp of last committed UI update

  // Optimized smoothing parameters for faster response
  const MIN_CONFIDENCE = 0.5; // Lowered for more sensitivity
  const WINDOW_SIZE = 3; // Smaller window for faster response
  const PERSISTENCE_REQUIRED = 1; // Only need 1 confident result for immediate update
  const MIN_CHANGE_INTERVAL_MS = 500; // Reduced to 0.5s for much faster updates

  const emotionIcons = {
    happy: Smile,
    sad: Frown,
    angry: AlertTriangle,
    fear: AlertTriangle,
    surprise: Eye,
    disgust: Meh,
    neutral: Meh
  };

  const emotionColors = {
    happy: 'text-green-500',
    sad: 'text-blue-500',
    angry: 'text-red-500',
    fear: 'text-purple-500',
    surprise: 'text-yellow-500',
    disgust: 'text-orange-500',
    neutral: 'text-gray-500'
  };

  const emotionBgColors = {
    happy: 'bg-green-100 border-green-300',
    sad: 'bg-blue-100 border-blue-300',
    angry: 'bg-red-100 border-red-300',
    fear: 'bg-purple-100 border-purple-300',
    surprise: 'bg-yellow-100 border-yellow-300',
    disgust: 'bg-orange-100 border-orange-300',
    neutral: 'bg-gray-100 border-gray-300'
  };

  useEffect(() => {
    return () => {
      stopStream();
    };
  }, []);

  // Ensure video element is ready
  useEffect(() => {
    if (videoRef.current && isStreaming) {
      videoRef.current.onloadedmetadata = () => {
        console.log('Video metadata loaded, ready for emotion detection');
      };
    }
  }, [isStreaming]);

  const startStream = async () => {
    try {
      setError(null);
      console.log('🎥 Starting camera stream...');
      
      // Check if getUserMedia is available
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        throw new Error('Camera access not supported');
      }
      
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { 
          width: { ideal: 640 }, 
          height: { ideal: 480 },
          facingMode: 'user'
        }
      });
      
      console.log('📹 Camera stream obtained:', stream);
      streamRef.current = stream;
      
      // Wait for video element to be ready
      if (videoRef.current) {
        console.log('🎬 Setting video source...');
        videoRef.current.srcObject = stream;
        setIsStreaming(true);
        
        // Start emotion detection after a short delay to ensure video is ready
        setTimeout(() => {
          console.log('🚀 Starting emotion detection...');
          startEmotionDetection();
        }, 1000);
      } else {
        console.error('❌ Video element not found');
        setError('Video element not available');
      }
    } catch (err) {
      console.error('❌ Camera error:', err);
      if (err.name === 'NotAllowedError') {
        setError('Camera access denied. Please allow camera permissions and try again.');
      } else if (err.name === 'NotFoundError') {
        setError('No camera found. Please connect a camera and try again.');
      } else {
        setError(`Failed to access camera: ${err.message}`);
      }
    }
  };

  const stopStream = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }
    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }
    setIsStreaming(false);
    stopEmotionDetection();
  };

  const startEmotionDetection = () => {
    if (detectionIntervalRef.current) return;
    
    detectionIntervalRef.current = setInterval(async () => {
      if (videoRef.current && isEnabled) {
        await detectEmotion();
      }
    }, 500); // Detect every 0.5 seconds for much faster response
  };

  const stopEmotionDetection = () => {
    if (detectionIntervalRef.current) {
      clearInterval(detectionIntervalRef.current);
      detectionIntervalRef.current = null;
    }
  };

  const detectEmotion = async () => {
    if (!videoRef.current || isDetecting) return;
    
    setIsDetecting(true);
    
    try {
      // Capture frame from video
      const canvas = canvasRef.current;
      const ctx = canvas.getContext('2d');
      canvas.width = videoRef.current.videoWidth;
      canvas.height = videoRef.current.videoHeight;
      ctx.drawImage(videoRef.current, 0, 0);
      
      // Convert to base64
      const imageData = canvas.toDataURL('image/jpeg', 0.8);
      
      // Send to backend
      const response = await fetch(`${API_BASE_URL}/api/emotion`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ image: imageData })
      });
      
      if (response.ok) {
        const result = await response.json();
        const { emotion, confidence: conf } = result;

        console.log('🎭 Emotion Detection Result:', { emotion, confidence: conf });

        // Push into rolling buffer
        const now = Date.now();
        const nextBuffer = [...resultsBufferRef.current, { emotion, confidence: conf, t: now }];
        // keep only last WINDOW_SIZE
        resultsBufferRef.current = nextBuffer.slice(-WINDOW_SIZE);

        // Filter by confidence
        const confident = resultsBufferRef.current.filter(r => r.confidence >= MIN_CONFIDENCE);

        // Compute stability: require last PERSISTENCE_REQUIRED confident results to agree
        let stableEmotion = null;
        let stableConfidence = 0;
        if (confident.length >= PERSISTENCE_REQUIRED) {
          const lastK = confident.slice(-PERSISTENCE_REQUIRED);
          const allSame = lastK.every(r => r.emotion === lastK[0].emotion);
          if (allSame) {
            stableEmotion = lastK[0].emotion;
            stableConfidence = lastK.reduce((s, r) => s + r.confidence, 0) / lastK.length;
          }
        }

        // Fallback to weighted majority over window when not strictly persistent
        if (!stableEmotion && confident.length >= 2) {
          const weights = confident.reduce((acc, r) => {
            acc[r.emotion] = (acc[r.emotion] || 0) + r.confidence;
            return acc;
          }, {});
          const entries = Object.entries(weights);
          entries.sort((a, b) => b[1] - a[1]);
          if (entries.length && entries[0][1] >= MIN_CONFIDENCE * 2) {
            stableEmotion = entries[0][0];
            // average confidence for chosen emotion
            const chosen = confident.filter(r => r.emotion === stableEmotion);
            stableConfidence = chosen.reduce((s, r) => s + r.confidence, 0) / chosen.length;
          }
        }

        // Update UI immediately for faster response - only debounce if same emotion
        const nowTs = Date.now();
        if (stableEmotion) {
          // Always update if emotion changed, or if enough time passed
          if (stableEmotion !== currentEmotion || (nowTs - lastUpdateRef.current >= MIN_CHANGE_INTERVAL_MS)) {
            setCurrentEmotion(stableEmotion);
            setConfidence(stableConfidence);
            lastUpdateRef.current = nowTs;

            const timestamp = new Date().toLocaleTimeString();
            const newEntry = { emotion: stableEmotion, confidence: stableConfidence, timestamp };
            setEmotionHistory(prev => [newEntry, ...prev.slice(0, 9)]);

            if (onEmotionDetected) {
              onEmotionDetected({ emotion: stableEmotion, confidence: stableConfidence });
            }
          }
        }
      } else {
        console.error('❌ Emotion detection failed:', response.status, await response.text());
      }
    } catch (err) {
      console.error('Emotion detection error:', err);
    } finally {
      setIsDetecting(false);
    }
  };

  const EmotionIcon = currentEmotion ? emotionIcons[currentEmotion] : Eye;
  const emotionColor = currentEmotion ? emotionColors[currentEmotion] : 'text-gray-500';
  const emotionBg = currentEmotion ? emotionBgColors[currentEmotion] : 'bg-gray-100 border-gray-300';

  return (
    <div className="bg-white rounded-xl shadow-lg p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-xl font-semibold text-gray-800 flex items-center gap-2">
          <Eye className="w-6 h-6 text-blue-600" />
          Live Emotion Detection
        </h3>
        <div className="flex gap-2">
          <button
            onClick={() => setShowHistory(!showHistory)}
            className="px-3 py-1 text-sm bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
          >
            {showHistory ? 'Hide' : 'Show'} History
          </button>
          {isStreaming ? (
            <button
              onClick={stopStream}
              className="px-4 py-2 bg-red-500 hover:bg-red-600 text-white rounded-lg flex items-center gap-2 transition-colors"
            >
              <CameraOff className="w-4 h-4" />
              Stop Camera
            </button>
          ) : (
            <button
              onClick={startStream}
              className="px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-lg flex items-center gap-2 transition-colors"
            >
              <Camera className="w-4 h-4" />
              Start Camera
            </button>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Video Feed */}
        <div className="space-y-4">
          <div className="relative bg-gray-100 rounded-lg overflow-hidden aspect-video">
            <video
              ref={videoRef}
              autoPlay
              muted
              playsInline
              className={`w-full h-full object-cover ${!isStreaming ? 'hidden' : ''}`}
            />
            {!isStreaming && (
              <div className="absolute inset-0 w-full h-full flex items-center justify-center text-gray-500">
                <div className="text-center">
                  <Camera className="w-12 h-12 mx-auto mb-2" />
                  <p>Camera not started</p>
                </div>
              </div>
            )}
            
            {/* Detection overlay */}
            {isDetecting && (
              <div className="absolute inset-0 bg-black bg-opacity-20 flex items-center justify-center">
                <motion.div
                  animate={{ rotate: 360 }}
                  transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                  className="w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full"
                />
              </div>
            )}
          </div>

          {/* Current Emotion Display */}
          <AnimatePresence>
            {currentEmotion && (
              <motion.div
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.8 }}
                className={`p-4 rounded-lg border-2 ${emotionBg}`}
              >
                <div className="flex items-center gap-3">
                  <EmotionIcon className={`w-8 h-8 ${emotionColor}`} />
                  <div>
                    <h4 className="font-semibold text-gray-800 capitalize">
                      {currentEmotion}
                    </h4>
                    <p className="text-sm text-gray-600">
                      Confidence: {(confidence * 100).toFixed(1)}%
                    </p>
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Emotion History */}
        <div className="space-y-4">
          <h4 className="font-semibold text-gray-800 flex items-center gap-2">
            <Heart className="w-5 h-5 text-red-500" />
            Recent Emotions
          </h4>
          
          {showHistory ? (
            <div className="space-y-2 max-h-64 overflow-y-auto">
              {emotionHistory.length > 0 ? (
                emotionHistory.map((entry, index) => {
                  const Icon = emotionIcons[entry.emotion];
                  const color = emotionColors[entry.emotion];
                  const bg = emotionBgColors[entry.emotion];
                  
                  return (
                    <motion.div
                      key={index}
                      initial={{ opacity: 0, x: 20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.1 }}
                      className={`p-3 rounded-lg border ${bg}`}
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <Icon className={`w-5 h-5 ${color}`} />
                          <span className="font-medium capitalize">{entry.emotion}</span>
                        </div>
                        <div className="text-right text-sm text-gray-600">
                          <div>{(entry.confidence * 100).toFixed(1)}%</div>
                          <div>{entry.timestamp}</div>
                        </div>
                      </div>
                    </motion.div>
                  );
                })
              ) : (
                <div className="text-center text-gray-500 py-8">
                  <Eye className="w-8 h-8 mx-auto mb-2" />
                  <p>No emotions detected yet</p>
                  <p className="text-sm">Start the camera to begin detection</p>
                </div>
              )}
            </div>
          ) : (
            <div className="text-center text-gray-500 py-8">
              <Eye className="w-8 h-8 mx-auto mb-2" />
              <p>Click "Show History" to see recent emotions</p>
            </div>
          )}
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="mt-4 p-3 bg-red-100 border border-red-300 rounded-lg text-red-700"
        >
          {error}
        </motion.div>
      )}

      {/* Hidden canvas for image capture */}
      <canvas ref={canvasRef} className="hidden" />
    </div>
  );
};

export default LiveEmotionDetector;
