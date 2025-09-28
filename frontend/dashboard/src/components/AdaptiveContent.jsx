import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { BookOpen, Lightbulb, Target, RefreshCw, Eye, Headphones, BookOpen as BookIcon } from 'lucide-react'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'https://neurolearn-6c0k.onrender.com';

export default function AdaptiveContent({ currentEmotion, userId, token }) {
  const [currentLesson, setCurrentLesson] = useState({
    id: 1,
    title: "Introduction to Machine Learning",
    content: "Machine learning is a subset of artificial intelligence that enables computers to learn and make decisions from data without being explicitly programmed.",
    difficulty: 0.5,
    estimatedTime: 15
  })

  const [adaptations, setAdaptations] = useState([])
  const [learningStyle, setLearningStyle] = useState(null)
  const [styleRecommendations, setStyleRecommendations] = useState([])

  const getAdaptation = (emotion) => {
    const adaptations = {
      happy: {
        message: "Great! You're feeling confident. Let's try something more challenging!",
        difficulty: 0.1,
        speed: 1.2,
        suggestion: "Try the advanced exercises",
        color: "green"
      },
      sad: {
        message: "I notice you might be struggling. Let's slow down and review the basics.",
        difficulty: -0.1,
        speed: 0.8,
        suggestion: "Take a break or review previous lessons",
        color: "blue"
      },
      angry: {
        message: "Take a deep breath. Let's try a different approach to this topic.",
        difficulty: -0.15,
        speed: 0.7,
        suggestion: "Switch to a different learning style",
        color: "red"
      },
      fear: {
        message: "It's okay to feel uncertain. Let's break this down into smaller steps.",
        difficulty: -0.2,
        speed: 0.6,
        suggestion: "Start with easier concepts",
        color: "purple"
      },
      surprise: {
        message: "Interesting! You seem surprised. Let's explore this concept further.",
        difficulty: 0.05,
        speed: 1.1,
        suggestion: "Dive deeper into this topic",
        color: "yellow"
      },
      disgust: {
        message: "I see this topic isn't resonating. Let's try a different angle.",
        difficulty: -0.1,
        speed: 0.9,
        suggestion: "Try a different subject area",
        color: "orange"
      },
      neutral: {
        message: "You seem focused. Let's continue at this pace.",
        difficulty: 0,
        speed: 1.0,
        suggestion: "Keep going with the current lesson",
        color: "gray"
      }
    }
    return adaptations[emotion] || adaptations.neutral
  }

  // Fetch learning style data
  useEffect(() => {
    if (userId && token) {
      fetchLearningStyle()
    }
  }, [userId, token])

  const fetchLearningStyle = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/learning-style/`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      })

      if (response.ok) {
        const data = await response.json()
        setLearningStyle(data.learning_style)
        
        // Fetch style-specific recommendations
        if (data.learning_style_opt_in) {
          fetchStyleRecommendations()
        }
      }
    } catch (err) {
      console.error('Failed to fetch learning style:', err)
    }
  }

  const fetchStyleRecommendations = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/learning-style/recommendations`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      })

      if (response.ok) {
        const data = await response.json()
        setStyleRecommendations(data.recommendations || [])
      }
    } catch (err) {
      console.error('Failed to fetch style recommendations:', err)
    }
  }

  useEffect(() => {
    if (currentEmotion) {
      const adaptation = getAdaptation(currentEmotion.emotion)
      
      // Update lesson difficulty
      setCurrentLesson(prev => ({
        ...prev,
        difficulty: Math.max(0, Math.min(1, prev.difficulty + adaptation.difficulty))
      }))

      // Add adaptation to history
      setAdaptations(prev => [{
        id: Date.now(),
        emotion: currentEmotion.emotion,
        message: adaptation.message,
        suggestion: adaptation.suggestion,
        color: adaptation.color,
        timestamp: new Date()
      }, ...prev.slice(0, 4)])

      // Auto-advance lesson after adaptation
      setTimeout(() => {
        setCurrentLesson(prev => ({
          ...prev,
          id: prev.id + 1,
          title: `Lesson ${prev.id + 1}: Advanced Concepts`,
          content: "Now that we've covered the basics, let's explore more advanced topics in machine learning algorithms and their applications."
        }))
      }, 3000)
    }
  }, [currentEmotion])

  const getDifficultyColor = (difficulty) => {
    if (difficulty < 0.3) return 'text-green-600 bg-green-100'
    if (difficulty < 0.7) return 'text-yellow-600 bg-yellow-100'
    return 'text-red-600 bg-red-100'
  }

  const getDifficultyText = (difficulty) => {
    if (difficulty < 0.3) return 'Easy'
    if (difficulty < 0.7) return 'Medium'
    return 'Hard'
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="card"
    >
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold text-gray-900">Adaptive Learning</h3>
        <div className="flex items-center space-x-2">
          <BookOpen className="w-5 h-5 text-gray-400" />
          <span className="text-sm text-gray-600">AI-Powered</span>
        </div>
      </div>

      {/* Current Lesson */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-3">
          <h4 className="text-lg font-medium text-gray-900">{currentLesson.title}</h4>
          <div className="flex items-center space-x-2">
            <span className={`px-2 py-1 rounded-full text-xs font-medium ${getDifficultyColor(currentLesson.difficulty)}`}>
              {getDifficultyText(currentLesson.difficulty)}
            </span>
            <span className="text-sm text-gray-500">{currentLesson.estimatedTime} min</span>
          </div>
        </div>
        
        <motion.p
          key={currentLesson.id}
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          className="text-gray-700 leading-relaxed mb-4"
        >
          {currentLesson.content}
        </motion.p>

        <div className="flex items-center justify-between">
          <div className="flex space-x-2">
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="btn-primary text-sm"
            >
              Start Lesson
            </motion.button>
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="btn-secondary text-sm"
            >
              Take Quiz
            </motion.button>
          </div>
          
          <div className="flex items-center space-x-2 text-sm text-gray-500">
            <Target className="w-4 h-4" />
            <span>Progress: 65%</span>
          </div>
        </div>
      </div>

      {/* Learning Style Recommendations */}
      {learningStyle && learningStyle.dominant_style && styleRecommendations.length > 0 && (
        <div className="mb-6">
          <div className="flex items-center space-x-2 mb-3">
            {learningStyle.dominant_style === 'visual' && <Eye className="w-4 h-4 text-blue-500" />}
            {learningStyle.dominant_style === 'auditory' && <Headphones className="w-4 h-4 text-green-500" />}
            {learningStyle.dominant_style === 'example' && <BookIcon className="w-4 h-4 text-purple-500" />}
            <h4 className="text-sm font-medium text-gray-700">
              Personalized for {learningStyle.dominant_style} learners
            </h4>
          </div>
          <div className="space-y-2">
            {styleRecommendations.slice(0, 3).map((recommendation, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
                className={`p-3 rounded-lg border-l-4 ${
                  learningStyle.dominant_style === 'visual' ? 'bg-blue-50 border-blue-400' :
                  learningStyle.dominant_style === 'auditory' ? 'bg-green-50 border-green-400' :
                  'bg-purple-50 border-purple-400'
                }`}
              >
                <p className="text-sm text-gray-700">{recommendation}</p>
              </motion.div>
            ))}
          </div>
        </div>
      )}

      {/* Recent Adaptations */}
      {adaptations.length > 0 && (
        <div>
          <h4 className="text-sm font-medium text-gray-700 mb-3">Recent Adaptations</h4>
          <div className="space-y-2">
            <AnimatePresence>
              {adaptations.map((adaptation) => (
                <motion.div
                  key={adaptation.id}
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: 0 }}
                  className={`p-3 rounded-lg border-l-4 ${
                    adaptation.color === 'green' ? 'bg-green-50 border-green-400' :
                    adaptation.color === 'blue' ? 'bg-blue-50 border-blue-400' :
                    adaptation.color === 'red' ? 'bg-red-50 border-red-400' :
                    adaptation.color === 'purple' ? 'bg-purple-50 border-purple-400' :
                    adaptation.color === 'yellow' ? 'bg-yellow-50 border-yellow-400' :
                    adaptation.color === 'orange' ? 'bg-orange-50 border-orange-400' :
                    'bg-gray-50 border-gray-400'
                  }`}
                >
                  <div className="flex items-start space-x-2">
                    <Lightbulb className={`w-4 h-4 mt-0.5 ${
                      adaptation.color === 'green' ? 'text-green-600' :
                      adaptation.color === 'blue' ? 'text-blue-600' :
                      adaptation.color === 'red' ? 'text-red-600' :
                      adaptation.color === 'purple' ? 'text-purple-600' :
                      adaptation.color === 'yellow' ? 'text-yellow-600' :
                      adaptation.color === 'orange' ? 'text-orange-600' :
                      'text-gray-600'
                    }`} />
                    <div className="flex-1">
                      <p className="text-sm font-medium text-gray-900 capitalize">
                        {adaptation.emotion} detected
                      </p>
                      <p className="text-sm text-gray-700">{adaptation.message}</p>
                      <p className="text-xs text-gray-500 mt-1">
                        💡 {adaptation.suggestion}
                      </p>
                    </div>
                  </div>
                </motion.div>
              ))}
            </AnimatePresence>
          </div>
        </div>
      )}
    </motion.div>
  )
}
