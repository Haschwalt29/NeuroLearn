import React from 'react'
import { motion } from 'framer-motion'
import { useEmotion } from '../contexts/EmotionContext'
import { Camera, CameraOff, Eye } from 'lucide-react'

export default function MoodIndicator({ currentEmotion, isCapturing }) {
  const { getEmotionColor, getEmotionIcon } = useEmotion()

  const getEmotionMessage = (emotion) => {
    const messages = {
      happy: "You're feeling great! Keep up the good work!",
      sad: "Don't worry, learning can be challenging. Take a break if needed.",
      angry: "Feeling frustrated? Let's try a different approach.",
      fear: "It's okay to feel uncertain. We'll take it step by step.",
      surprise: "Interesting! Your curiosity is showing.",
      disgust: "This topic isn't resonating. Let's try something else.",
      neutral: "You're focused and ready to learn."
    }
    return messages[emotion] || "Let's see how you're feeling today!"
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="card"
    >
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">Mood Indicator</h3>
        <div className="flex items-center space-x-2">
          {/* Development Mode Indicator */}
          <div className="flex items-center gap-1 px-2 py-1 bg-green-100 text-green-700 rounded-full text-xs">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
            <span>Live Detection</span>
          </div>
          {isCapturing ? (
            <Camera className="w-5 h-5 text-green-500" />
          ) : (
            <CameraOff className="w-5 h-5 text-gray-400" />
          )}
          <span className="text-sm text-gray-600">
            {isCapturing ? 'Active' : 'Inactive'}
          </span>
        </div>
      </div>

      {currentEmotion ? (
        <motion.div
          initial={{ scale: 0.8, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ type: "spring", stiffness: 200 }}
          className="text-center"
        >
          <motion.div
            animate={{ 
              scale: [1, 1.1, 1],
              rotate: [0, 5, -5, 0]
            }}
            transition={{ 
              duration: 2,
              repeat: Infinity,
              ease: "easeInOut"
            }}
            className="w-20 h-20 mx-auto mb-4 rounded-full flex items-center justify-center text-4xl"
            style={{ 
              backgroundColor: getEmotionColor(currentEmotion.emotion) + '20',
              border: `3px solid ${getEmotionColor(currentEmotion.emotion)}`
            }}
          >
            {getEmotionIcon(currentEmotion.emotion)}
          </motion.div>

          <motion.h4
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.2 }}
            className="text-xl font-bold mb-2 capitalize"
            style={{ color: getEmotionColor(currentEmotion.emotion) }}
          >
            {currentEmotion.emotion}
          </motion.h4>

          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.4 }}
            className="text-sm text-gray-600 mb-2"
          >
            Confidence: {Math.round(currentEmotion.confidence)}%
          </motion.p>

          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.6 }}
            className="text-sm text-gray-700 italic"
          >
            {getEmotionMessage(currentEmotion.emotion)}
          </motion.p>

          <motion.div
            initial={{ width: 0 }}
            animate={{ width: `${currentEmotion.confidence}%` }}
            transition={{ delay: 0.8, duration: 0.5 }}
            className="h-2 bg-gray-200 rounded-full mt-4 overflow-hidden"
          >
            <div
              className="h-full rounded-full transition-all duration-300"
              style={{ 
                backgroundColor: getEmotionColor(currentEmotion.emotion),
                width: '100%'
              }}
            />
          </motion.div>
        </motion.div>
      ) : (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="text-center py-8"
        >
          <motion.div
            animate={{ 
              scale: [1, 1.05, 1],
              opacity: [0.5, 1, 0.5]
            }}
            transition={{ 
              duration: 2,
              repeat: Infinity,
              ease: "easeInOut"
            }}
            className="w-20 h-20 mx-auto mb-4 rounded-full bg-gray-100 flex items-center justify-center"
          >
            <Eye className="w-8 h-8 text-gray-400" />
          </motion.div>
          
          <p className="text-gray-500 mb-2">No emotion detected yet</p>
          <p className="text-sm text-gray-400">
            {isCapturing ? 'Looking for your face...' : 'Start detection to see your mood'}
          </p>
        </motion.div>
      )}
    </motion.div>
  )
}
