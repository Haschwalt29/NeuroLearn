import React, { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import axios from 'axios'
import { useAuth } from '../../contexts/AuthContext'
import { useSocket } from '../../contexts/SocketContext'
import { BookOpen, Clock, Star, CheckCircle, PlayCircle, Calendar, Sparkles } from 'lucide-react'

export default function AdaptivePath() {
  const { token } = useAuth()
  const { on } = useSocket()
  const [learningPath, setLearningPath] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [stats, setStats] = useState(null)

  useEffect(() => {
    fetchLearningPath()
    fetchStats()
  }, [token])

  useEffect(() => {
    const handler = (payload) => {
      if (payload.updates) {
        // Refresh learning path when curriculum updates
        fetchLearningPath()
        fetchStats()
      }
    }
    on('curriculum_update', handler)
    return () => {}
  }, [on])

  const fetchLearningPath = async () => {
    try {
      setLoading(true)
      const response = await axios.get('/api/curriculum/path', {
        headers: { Authorization: `Bearer ${token}` }
      })
      setLearningPath(response.data.learning_path || [])
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const fetchStats = async () => {
    try {
      const response = await axios.get('/api/curriculum/stats', {
        headers: { Authorization: `Bearer ${token}` }
      })
      setStats(response.data.stats)
    } catch (err) {
      console.error('Failed to fetch stats:', err)
    }
  }

  const updateProgress = async (lessonId, progress) => {
    try {
      await axios.post(`/api/curriculum/path/${lessonId}/progress`, 
        { progress }, 
        { headers: { Authorization: `Bearer ${token}` } }
      )
      fetchLearningPath()
    } catch (err) {
      console.error('Failed to update progress:', err)
    }
  }

  const completeLesson = async (lessonId) => {
    try {
      await axios.post(`/api/curriculum/path/${lessonId}/complete`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      })
      fetchLearningPath()
      fetchStats()
    } catch (err) {
      console.error('Failed to complete lesson:', err)
    }
  }

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-green-600" />
      case 'in-progress':
        return <PlayCircle className="w-5 h-5 text-blue-600" />
      default:
        return <BookOpen className="w-5 h-5 text-gray-400" />
    }
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800 border-green-200'
      case 'in-progress':
        return 'bg-blue-100 text-blue-800 border-blue-200'
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200'
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="text-center py-8 text-red-500">
        Error loading learning path: {error}
      </div>
    )
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-6"
    >
      {/* Stats Overview */}
      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-white p-4 rounded-lg border border-gray-200">
            <div className="text-2xl font-bold text-blue-600">{stats.total_lessons}</div>
            <div className="text-sm text-gray-600">Total Lessons</div>
          </div>
          <div className="bg-white p-4 rounded-lg border border-gray-200">
            <div className="text-2xl font-bold text-green-600">{stats.completed_lessons}</div>
            <div className="text-sm text-gray-600">Completed</div>
          </div>
          <div className="bg-white p-4 rounded-lg border border-gray-200">
            <div className="text-2xl font-bold text-yellow-600">{stats.fresh_lessons}</div>
            <div className="text-sm text-gray-600">Fresh Lessons</div>
          </div>
          <div className="bg-white p-4 rounded-lg border border-gray-200">
            <div className="text-2xl font-bold text-purple-600">{Math.round(stats.completion_rate)}%</div>
            <div className="text-sm text-gray-600">Completion Rate</div>
          </div>
        </div>
      )}

      <div className="flex items-center gap-3">
        <BookOpen className="w-6 h-6 text-blue-600" />
        <h2 className="text-2xl font-bold text-gray-800">Your Learning Path</h2>
        <span className="bg-blue-100 text-blue-800 text-sm px-2 py-1 rounded-full">
          {learningPath.length} lessons
        </span>
      </div>

      {learningPath.length === 0 ? (
        <div className="text-center py-12 text-gray-500">
          <BookOpen className="w-16 h-16 mx-auto mb-4 text-gray-300" />
          <p className="text-lg">No lessons in your learning path yet</p>
          <p className="text-sm">Lessons will be added based on your learning progress and weak areas</p>
        </div>
      ) : (
        <div className="space-y-4">
          {learningPath.map((lesson, index) => (
            <motion.div
              key={lesson.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
              className={`bg-white rounded-lg border-2 p-6 ${lesson.is_new ? 'border-purple-200 bg-purple-50' : 'border-gray-200'}`}
            >
              <div className="flex items-start gap-4">
                <div className="flex-shrink-0">
                  {getStatusIcon(lesson.status)}
                </div>
                
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <h3 className="text-lg font-semibold text-gray-800">{lesson.title}</h3>
                    {lesson.is_new && (
                      <span className="bg-purple-100 text-purple-800 text-xs px-2 py-1 rounded-full flex items-center gap-1">
                        <Sparkles className="w-3 h-3" />
                        New
                      </span>
                    )}
                    <span className={`px-2 py-1 rounded-full text-xs font-medium border ${getStatusColor(lesson.status)}`}>
                      {lesson.status.replace('-', ' ').toUpperCase()}
                    </span>
                  </div>
                  
                  <p className="text-gray-600 mb-3">{lesson.summary}</p>
                  
                  <div className="flex items-center gap-4 text-sm text-gray-500 mb-4">
                    <div className="flex items-center gap-1">
                      <Clock className="w-4 h-4" />
                      {lesson.estimated_time} min
                    </div>
                    <div className="flex items-center gap-1">
                      <Star className="w-4 h-4" />
                      {Math.round(lesson.difficulty * 5)}/5 difficulty
                    </div>
                    <div className="flex items-center gap-1">
                      <Calendar className="w-4 h-4" />
                      Priority {lesson.priority}
                    </div>
                  </div>
                  
                  {lesson.tags && lesson.tags.length > 0 && (
                    <div className="flex flex-wrap gap-1 mb-4">
                      {lesson.tags.slice(0, 5).map((tag, i) => (
                        <span key={i} className="bg-gray-100 text-gray-600 text-xs px-2 py-1 rounded">
                          {tag}
                        </span>
                      ))}
                    </div>
                  )}
                  
                  {lesson.replaced_from && (
                    <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3 mb-4">
                      <p className="text-sm text-yellow-800">
                        <strong>Updated:</strong> {lesson.replacement_reason}
                      </p>
                    </div>
                  )}
                  
                  {/* Progress Bar for In-Progress Lessons */}
                  {lesson.status === 'in-progress' && (
                    <div className="mb-4">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm font-medium text-gray-700">Progress</span>
                        <span className="text-sm text-gray-500">{Math.round(lesson.progress * 100)}%</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <motion.div 
                          className="bg-blue-500 h-2 rounded-full"
                          initial={{ width: 0 }}
                          animate={{ width: `${lesson.progress * 100}%` }}
                          transition={{ duration: 0.5 }}
                        ></motion.div>
                      </div>
                      <div className="flex gap-2 mt-2">
                        <button
                          onClick={() => updateProgress(lesson.lesson_id, Math.min(1, lesson.progress + 0.1))}
                          className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded hover:bg-blue-200"
                        >
                          +10%
                        </button>
                        <button
                          onClick={() => completeLesson(lesson.lesson_id)}
                          className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded hover:bg-green-200"
                        >
                          Complete
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      )}
    </motion.div>
  )
}
