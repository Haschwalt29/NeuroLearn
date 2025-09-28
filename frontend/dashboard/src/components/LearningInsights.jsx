import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { TrendingUp, TrendingDown, Minus, Eye, Headphones, BookOpen, Target, AlertCircle, CheckCircle } from 'lucide-react'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'https://neurolearn-6c0k.onrender.com';

export default function LearningInsights({ userId, token, className = '' }) {
  const [insights, setInsights] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchInsights()
  }, [userId, token])

  const fetchInsights = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/personalization/insights`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      })
      
      if (response.ok) {
        const data = await response.json()
        setInsights(data)
      }
    } catch (error) {
      console.error('Failed to fetch insights:', error)
    } finally {
      setLoading(false)
    }
  }

  const getTrendIcon = (trend) => {
    switch (trend) {
      case 'improving': return TrendingUp
      case 'declining': return TrendingDown
      default: return Minus
    }
  }

  const getTrendColor = (trend) => {
    switch (trend) {
      case 'improving': return 'text-green-600'
      case 'declining': return 'text-red-600'
      default: return 'text-gray-600'
    }
  }

  const getMasteryColor = (score) => {
    if (score >= 80) return 'text-green-600 bg-green-100'
    if (score >= 60) return 'text-yellow-600 bg-yellow-100'
    if (score >= 40) return 'text-orange-600 bg-orange-100'
    return 'text-red-600 bg-red-100'
  }

  const getLearningStyleIcon = (style) => {
    switch (style) {
      case 'visual': return Eye
      case 'auditory': return Headphones
      case 'example': return BookOpen
      default: return Target
    }
  }

  if (loading) {
    return (
      <div className={`bg-white rounded-lg shadow-sm p-6 ${className}`}>
        <div className="animate-pulse">
          <div className="h-6 bg-gray-200 rounded w-1/3 mb-4"></div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="bg-gray-200 rounded-lg p-4 h-32"></div>
            <div className="bg-gray-200 rounded-lg p-4 h-32"></div>
          </div>
        </div>
      </div>
    )
  }

  if (!insights) {
    return (
      <div className={`bg-white rounded-lg shadow-sm p-6 ${className}`}>
        <p className="text-gray-500">Failed to load learning insights</p>
      </div>
    )
  }

  const { mastery_summary, topic_categories, learning_style, performance_trends, emotion_patterns, recommendations } = insights

  return (
    <div className={`bg-white rounded-lg shadow-sm p-6 ${className}`}>
      {/* Header */}
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Learning Insights</h2>
        <p className="text-gray-600">Your personalized learning analysis and recommendations</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Mastery Overview */}
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-gray-900">Mastery Overview</h3>
          
          {/* Mastery Stats */}
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-gray-50 rounded-lg p-4">
              <div className="text-2xl font-bold text-gray-900">{mastery_summary.total_topics}</div>
              <div className="text-sm text-gray-600">Total Topics</div>
            </div>
            <div className="bg-gray-50 rounded-lg p-4">
              <div className="text-2xl font-bold text-gray-900">{Math.round(mastery_summary.average_mastery)}%</div>
              <div className="text-sm text-gray-600">Avg Mastery</div>
            </div>
          </div>

          {/* Topic Categories */}
          <div className="space-y-3">
            <h4 className="text-md font-semibold text-gray-900">Topic Categories</h4>
            
            {/* Weak Topics */}
            {topic_categories.weak.length > 0 && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-3">
                <div className="flex items-center space-x-2 mb-2">
                  <AlertCircle className="w-4 h-4 text-red-600" />
                  <span className="text-sm font-semibold text-red-800">Weak Areas ({topic_categories.weak.length})</span>
                </div>
                <div className="space-y-1">
                  {topic_categories.weak.slice(0, 3).map((topic, index) => (
                    <div key={index} className="flex items-center justify-between text-sm">
                      <span className="text-red-700">{topic.topic}</span>
                      <span className="text-red-600 font-medium">{Math.round(topic.score)}%</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Strong Topics */}
            {topic_categories.strong.length > 0 && (
              <div className="bg-green-50 border border-green-200 rounded-lg p-3">
                <div className="flex items-center space-x-2 mb-2">
                  <CheckCircle className="w-4 h-4 text-green-600" />
                  <span className="text-sm font-semibold text-green-800">Strong Areas ({topic_categories.strong.length})</span>
                </div>
                <div className="space-y-1">
                  {topic_categories.strong.slice(0, 3).map((topic, index) => (
                    <div key={index} className="flex items-center justify-between text-sm">
                      <span className="text-green-700">{topic.topic}</span>
                      <span className="text-green-600 font-medium">{Math.round(topic.score)}%</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Learning Style & Performance */}
        <div className="space-y-4">
          {/* Learning Style */}
          {learning_style && (
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-3">Learning Style</h3>
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <div className="flex items-center space-x-3 mb-3">
                  {React.createElement(getLearningStyleIcon(learning_style.dominant_style), {
                    className: "w-6 h-6 text-blue-600"
                  })}
                  <div>
                    <div className="font-semibold text-blue-900">
                      {learning_style.dominant_style?.charAt(0).toUpperCase() + learning_style.dominant_style?.slice(1)} Learner
                    </div>
                    <div className="text-sm text-blue-700">
                      Based on {learning_style.total_attempts} learning sessions
                    </div>
                  </div>
                </div>
                
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>Visual</span>
                    <span>{Math.round(learning_style.visual_score * 100)}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <motion.div
                      className="bg-blue-500 h-2 rounded-full"
                      initial={{ width: 0 }}
                      animate={{ width: `${learning_style.visual_score * 100}%` }}
                      transition={{ duration: 1 }}
                    />
                  </div>
                  
                  <div className="flex justify-between text-sm">
                    <span>Auditory</span>
                    <span>{Math.round(learning_style.auditory_score * 100)}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <motion.div
                      className="bg-green-500 h-2 rounded-full"
                      initial={{ width: 0 }}
                      animate={{ width: `${learning_style.auditory_score * 100}%` }}
                      transition={{ duration: 1, delay: 0.2 }}
                    />
                  </div>
                  
                  <div className="flex justify-between text-sm">
                    <span>Example-based</span>
                    <span>{Math.round(learning_style.example_score * 100)}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <motion.div
                      className="bg-purple-500 h-2 rounded-full"
                      initial={{ width: 0 }}
                      animate={{ width: `${learning_style.example_score * 100}%` }}
                      transition={{ duration: 1, delay: 0.4 }}
                    />
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Performance Trends */}
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-3">Performance Trends</h3>
            <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
              <div className="flex items-center space-x-2 mb-3">
                {React.createElement(getTrendIcon(performance_trends.trend), {
                  className: `w-5 h-5 ${getTrendColor(performance_trends.trend)}`
                })}
                <span className={`font-semibold ${getTrendColor(performance_trends.trend)}`}>
                  {performance_trends.trend.charAt(0).toUpperCase() + performance_trends.trend.slice(1)}
                </span>
              </div>
              
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <div className="text-gray-600">Average Score</div>
                  <div className="font-semibold text-gray-900">
                    {Math.round(performance_trends.average_score * 100)}%
                  </div>
                </div>
                <div>
                  <div className="text-gray-600">Total Attempts</div>
                  <div className="font-semibold text-gray-900">
                    {performance_trends.total_attempts}
                  </div>
                </div>
              </div>
              
              {performance_trends.improvement_rate !== 0 && (
                <div className="mt-3 text-sm">
                  <span className="text-gray-600">Improvement Rate: </span>
                  <span className={`font-semibold ${performance_trends.improvement_rate > 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {performance_trends.improvement_rate > 0 ? '+' : ''}{Math.round(performance_trends.improvement_rate * 100)}%
                  </span>
                </div>
              )}
            </div>
          </div>

          {/* Emotion Patterns */}
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-3">Emotion Patterns</h3>
            <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
              <div className="text-sm mb-2">
                <span className="text-gray-600">Dominant Emotion: </span>
                <span className="font-semibold text-gray-900 capitalize">
                  {emotion_patterns.dominant_emotion}
                </span>
              </div>
              
              <div className="text-sm mb-2">
                <span className="text-gray-600">Trend: </span>
                <span className={`font-semibold ${
                  emotion_patterns.trend === 'more_positive' ? 'text-green-600' :
                  emotion_patterns.trend === 'more_negative' ? 'text-red-600' : 'text-gray-600'
                }`}>
                  {emotion_patterns.trend.replace('_', ' ')}
                </span>
              </div>
              
              <div className="text-sm">
                <span className="text-gray-600">Total Sessions: </span>
                <span className="font-semibold text-gray-900">
                  {emotion_patterns.total_logs}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Recommendations */}
      {recommendations.length > 0 && (
        <div className="mt-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-3">Personalized Recommendations</h3>
          <div className="space-y-2">
            {recommendations.map((rec, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
                className="bg-blue-50 border border-blue-200 rounded-lg p-3"
              >
                <div className="flex items-start space-x-2">
                  <div className={`w-2 h-2 rounded-full mt-2 ${
                    rec.priority === 'high' ? 'bg-red-500' :
                    rec.priority === 'medium' ? 'bg-yellow-500' : 'bg-green-500'
                  }`} />
                  <div>
                    <div className="font-semibold text-blue-900 text-sm">
                      {rec.title}
                    </div>
                    <div className="text-blue-700 text-sm">
                      {rec.description}
                    </div>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
