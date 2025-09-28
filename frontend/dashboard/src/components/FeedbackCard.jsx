import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

const FeedbackCard = ({ feedback, onClose, autoClose = true }) => {
  const [displayedText, setDisplayedText] = useState('');
  const [isVisible, setIsVisible] = useState(true);

  useEffect(() => {
    if (!feedback?.feedback_text) return;

    // Typewriter effect
    let index = 0;
    const text = feedback.feedback_text;
    const interval = setInterval(() => {
      if (index < text.length) {
        setDisplayedText(text.slice(0, index + 1));
        index++;
      } else {
        clearInterval(interval);
        // Auto close after 8 seconds if enabled
        if (autoClose) {
          setTimeout(() => {
            setIsVisible(false);
            setTimeout(() => onClose?.(), 500); // Wait for animation to complete
          }, 8000);
        }
      }
    }, 30); // 30ms per character for smooth typing

    return () => clearInterval(interval);
  }, [feedback?.feedback_text, autoClose, onClose]);

  const getEmotionColor = (emotion) => {
    const colors = {
      happy: 'from-yellow-400 to-orange-500',
      sad: 'from-blue-400 to-blue-600',
      angry: 'from-red-400 to-red-600',
      fear: 'from-purple-400 to-purple-600',
      surprise: 'from-green-400 to-green-600',
      disgust: 'from-gray-400 to-gray-600',
      neutral: 'from-indigo-400 to-indigo-600',
      focused: 'from-teal-400 to-teal-600',
      frustrated: 'from-red-400 to-red-600'
    };
    return colors[emotion] || colors.neutral;
  };

  const getPerformanceLevel = (accuracy) => {
    if (accuracy >= 80) return 'excellent';
    if (accuracy >= 60) return 'good';
    return 'needs_improvement';
  };

  const performanceLevel = getPerformanceLevel(feedback?.performance_summary?.accuracy || 0);
  const dominantEmotion = feedback?.emotion_context?.dominant_emotion || 'neutral';

  return (
    <AnimatePresence>
      {isVisible && (
        <motion.div
          initial={{ opacity: 0, y: 50, scale: 0.9 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          exit={{ opacity: 0, y: -50, scale: 0.9 }}
          transition={{ duration: 0.5, ease: "easeOut" }}
          className="fixed top-4 right-4 z-50 max-w-md"
        >
          <div className={`bg-gradient-to-r ${getEmotionColor(dominantEmotion)} rounded-lg shadow-2xl p-6 text-white relative overflow-hidden`}>
            {/* Background pattern */}
            <div className="absolute inset-0 opacity-10">
              <div className="absolute top-0 right-0 w-32 h-32 bg-white rounded-full -translate-y-16 translate-x-16"></div>
              <div className="absolute bottom-0 left-0 w-24 h-24 bg-white rounded-full translate-y-12 -translate-x-12"></div>
            </div>

            {/* Header */}
            <div className="relative z-10 flex items-center justify-between mb-4">
              <div className="flex items-center space-x-2">
                <div className="w-8 h-8 bg-white bg-opacity-20 rounded-full flex items-center justify-center">
                  <span className="text-lg">
                    {performanceLevel === 'excellent' ? '🎉' : 
                     performanceLevel === 'good' ? '👍' : '💪'}
                  </span>
                </div>
                <h3 className="font-bold text-lg">Personalized Feedback</h3>
              </div>
              <button
                onClick={() => {
                  setIsVisible(false);
                  setTimeout(() => onClose?.(), 500);
                }}
                className="text-white hover:text-gray-200 transition-colors"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            {/* Feedback text with typewriter effect */}
            <div className="relative z-10 mb-4">
              <p className="text-sm leading-relaxed min-h-[3rem]">
                {displayedText}
                <motion.span
                  animate={{ opacity: [1, 0, 1] }}
                  transition={{ duration: 0.8, repeat: Infinity }}
                  className="inline-block w-1 h-4 bg-white ml-1"
                />
              </p>
            </div>

            {/* Performance summary */}
            {feedback?.performance_summary && (
              <div className="relative z-10 bg-white bg-opacity-10 rounded-lg p-3 mb-4">
                <h4 className="font-semibold text-sm mb-2">Performance Summary</h4>
                <div className="grid grid-cols-2 gap-2 text-xs">
                  <div>
                    <span className="opacity-75">Accuracy:</span>
                    <span className="ml-1 font-semibold">
                      {feedback.performance_summary.accuracy.toFixed(1)}%
                    </span>
                  </div>
                  <div>
                    <span className="opacity-75">Questions:</span>
                    <span className="ml-1 font-semibold">
                      {feedback.performance_summary.total_questions}
                    </span>
                  </div>
                  {feedback.performance_summary.strong_topics?.length > 0 && (
                    <div className="col-span-2">
                      <span className="opacity-75">Strong in:</span>
                      <span className="ml-1 font-semibold">
                        {feedback.performance_summary.strong_topics.join(', ')}
                      </span>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Emotion indicator */}
            <div className="relative z-10 flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <span className="text-xs opacity-75">Current mood:</span>
                <span className="text-sm font-semibold capitalize">
                  {dominantEmotion.replace('_', ' ')}
                </span>
              </div>
              <div className="flex space-x-1">
                {feedback?.learning_trends?.streak_days > 0 && (
                  <div className="bg-white bg-opacity-20 rounded-full px-2 py-1">
                    <span className="text-xs font-semibold">
                      🔥 {feedback.learning_trends.streak_days}d streak
                    </span>
                  </div>
                )}
              </div>
            </div>

            {/* Progress bar for auto-close */}
            {autoClose && (
              <motion.div
                initial={{ width: '100%' }}
                animate={{ width: '0%' }}
                transition={{ duration: 8, ease: "linear" }}
                className="absolute bottom-0 left-0 h-1 bg-white bg-opacity-30"
              />
            )}
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
};

export default FeedbackCard;
