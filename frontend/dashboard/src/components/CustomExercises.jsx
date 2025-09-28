import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Target, Clock, Star, BookOpen, Headphones, Eye, Play } from 'lucide-react'

export default function CustomExercises({ userId, token, topic = null, className = '' }) {
  const [exercises, setExercises] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchExercises()
  }, [userId, token, topic])

  const fetchExercises = async () => {
    try {
      const url = topic 
        ? `/api/personalization/custom-exercises?topic=${encodeURIComponent(topic)}`
        : '/api/personalization/custom-exercises'
      
      const response = await fetch(url, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      })
      
      if (response.ok) {
        const data = await response.json()
        setExercises(data.exercises)
      }
    } catch (error) {
      console.error('Failed to fetch custom exercises:', error)
    } finally {
      setLoading(false)
    }
  }

  const getExerciseTypeIcon = (type) => {
    switch (type) {
      case 'diagram_analysis': return Eye
      case 'audio_explanation': return Headphones
      case 'practical_example': return BookOpen
      default: return Target
    }
  }

  const getExerciseTypeColor = (type) => {
    switch (type) {
      case 'diagram_analysis': return 'from-blue-500 to-cyan-500'
      case 'audio_explanation': return 'from-green-500 to-emerald-500'
      case 'practical_example': return 'from-purple-500 to-pink-500'
      default: return 'from-gray-500 to-gray-600'
    }
  }

  const getPriorityColor = (priority) => {
    if (priority > 0.7) return 'text-red-600 bg-red-100'
    if (priority > 0.4) return 'text-yellow-600 bg-yellow-100'
    return 'text-green-600 bg-green-100'
  }

  const startExercise = (exerciseId) => {
    // This would typically open the exercise or navigate to it
    console.log('Starting exercise:', exerciseId)
    // You could emit a socket event or navigate to the exercise page
  }

  if (loading) {
    return (
      <div className={`bg-white rounded-lg shadow-sm p-6 ${className}`}>
        <div className="animate-pulse">
          <div className="h-6 bg-gray-200 rounded w-1/3 mb-4"></div>
          <div className="space-y-3">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="bg-gray-200 rounded-lg p-4 h-24"></div>
            ))}
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className={`bg-white rounded-lg shadow-sm p-6 ${className}`}>
      {/* Header */}
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Custom Exercises</h2>
        <p className="text-gray-600">
          Personalized exercises based on your learning style and weak areas
          {topic && ` for ${topic}`}
        </p>
      </div>

      {/* Exercises List */}
      <div className="space-y-4">
        {exercises.length > 0 ? (
          exercises.map((exercise, index) => {
            const ExerciseIcon = getExerciseTypeIcon(exercise.type)
            const exerciseColor = getExerciseTypeColor(exercise.type)

            return (
              <motion.div
                key={exercise.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-start space-x-4 flex-1">
                    {/* Exercise Icon */}
                    <div className={`w-12 h-12 rounded-lg bg-gradient-to-r ${exerciseColor} flex items-center justify-center text-white flex-shrink-0`}>
                      <ExerciseIcon className="w-6 h-6" />
                    </div>

                    {/* Exercise Content */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center space-x-2 mb-2">
                        <h3 className="text-lg font-semibold text-gray-900 truncate">
                          {exercise.question}
                        </h3>
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${getPriorityColor(exercise.priority)}`}>
                          Priority: {Math.round(exercise.priority * 100)}%
                        </span>
                      </div>
                      
                      <div className="flex items-center space-x-4 text-sm text-gray-600 mb-3">
                        <div className="flex items-center space-x-1">
                          <Target className="w-4 h-4" />
                          <span>{exercise.topic}</span>
                        </div>
                        <div className="flex items-center space-x-1">
                          <Clock className="w-4 h-4" />
                          <span>{exercise.estimated_time} min</span>
                        </div>
                        <div className="flex items-center space-x-1">
                          <Star className="w-4 h-4" />
                          <span className="capitalize">{exercise.type.replace('_', ' ')}</span>
                        </div>
                      </div>

                      <div className="text-sm text-gray-700">
                        Difficulty: {Math.round(exercise.difficulty * 100)}%
                      </div>
                    </div>
                  </div>

                  {/* Start Button */}
                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={() => startExercise(exercise.id)}
                    className={`ml-4 px-4 py-2 bg-gradient-to-r ${exerciseColor} text-white rounded-lg font-medium hover:shadow-lg transition-shadow flex items-center space-x-2`}
                  >
                    <Play className="w-4 h-4" />
                    <span>Start</span>
                  </motion.button>
                </div>
              </motion.div>
            )
          })
        ) : (
          <div className="text-center py-12">
            <div className="w-16 h-16 mx-auto mb-4 bg-gray-100 rounded-full flex items-center justify-center">
              <Target className="w-8 h-8 text-gray-400" />
            </div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              No custom exercises available
            </h3>
            <p className="text-gray-500">
              {topic 
                ? `Complete more activities in ${topic} to generate personalized exercises.`
                : 'Complete more activities to generate personalized exercises based on your learning style.'
              }
            </p>
          </div>
        )}
      </div>

      {/* Exercise Type Legend */}
      {exercises.length > 0 && (
        <div className="mt-6 pt-6 border-t border-gray-200">
          <h4 className="text-sm font-semibold text-gray-900 mb-3">Exercise Types</h4>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
            <div className="flex items-center space-x-2">
              <div className="w-4 h-4 bg-gradient-to-r from-blue-500 to-cyan-500 rounded"></div>
              <span className="text-gray-700">Visual (Diagram Analysis)</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-4 h-4 bg-gradient-to-r from-green-500 to-emerald-500 rounded"></div>
              <span className="text-gray-700">Auditory (Audio Explanation)</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-4 h-4 bg-gradient-to-r from-purple-500 to-pink-500 rounded"></div>
              <span className="text-gray-700">Example-based (Practical)</span>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
