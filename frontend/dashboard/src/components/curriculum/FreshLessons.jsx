import React, { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import axios from 'axios'
import { useAuth } from '../../contexts/AuthContext'
import { useSocket } from '../../contexts/SocketContext'
import { BookOpen, Clock, Star, Tag, Sparkles, ArrowRight } from 'lucide-react'

export default function FreshLessons() {
  const { token } = useAuth()
  const { on } = useSocket()
  const [freshLessons, setFreshLessons] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchFreshLessons()
  }, [token])

  useEffect(() => {
    const handler = (payload) => {
      if (payload.updates) {
        // Refresh fresh lessons when curriculum updates
        fetchFreshLessons()
      }
    }
    on('curriculum_update', handler)
    return () => {}
  }, [on])

  const fetchFreshLessons = async () => {
    try {
      setLoading(true)
      const response = await axios.get('/api/curriculum/fresh-lessons', {
        headers: { Authorization: `Bearer ${token}` }
      })
      setFreshLessons(response.data.fresh_lessons || [])
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const startLesson = async (lessonId) => {
    try {
      await axios.post(`/api/curriculum/path/${lessonId}/start`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      })
      // Refresh the list
      fetchFreshLessons()
    } catch (err) {
      console.error('Failed to start lesson:', err)
    }
  }

  const getDifficultyColor = (difficulty) => {
    if (difficulty < 0.3) return 'text-green-600 bg-green-100'
    if (difficulty < 0.7) return 'text-yellow-600 bg-yellow-100'
    return 'text-red-600 bg-red-100'
  }

  const getDifficultyText = (difficulty) => {
    if (difficulty < 0.3) return 'Beginner'
    if (difficulty < 0.7) return 'Intermediate'
    return 'Advanced'
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
        Error loading fresh lessons: {error}
      </div>
    )
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-6"
    >
      <div className="flex items-center gap-3">
        <Sparkles className="w-6 h-6 text-purple-600" />
        <h2 className="text-2xl font-bold text-gray-800">Fresh Lessons</h2>
        <span className="bg-purple-100 text-purple-800 text-sm px-2 py-1 rounded-full">
          {freshLessons.length} new
        </span>
      </div>

      {freshLessons.length === 0 ? (
        <div className="text-center py-12 text-gray-500">
          <BookOpen className="w-16 h-16 mx-auto mb-4 text-gray-300" />
          <p className="text-lg">No fresh lessons available yet</p>
          <p className="text-sm">New lessons will appear here as they're added to your curriculum</p>
        </div>
      ) : (
        <div className="grid gap-4">
          {freshLessons.map((lesson, index) => (
            <motion.div
              key={lesson.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
              className="bg-white rounded-lg border border-gray-200 p-6 hover:shadow-md transition-shadow"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <h3 className="text-lg font-semibold text-gray-800">{lesson.title}</h3>
                    {lesson.is_new && (
                      <span className="bg-green-100 text-green-800 text-xs px-2 py-1 rounded-full flex items-center gap-1">
                        <Sparkles className="w-3 h-3" />
                        New
                      </span>
                    )}
                  </div>
                  
                  <p className="text-gray-600 mb-3 line-clamp-2">{lesson.summary}</p>
                  
                  <div className="flex items-center gap-4 text-sm text-gray-500 mb-4">
                    <div className="flex items-center gap-1">
                      <Clock className="w-4 h-4" />
                      {lesson.estimated_time} min
                    </div>
                    <div className={`px-2 py-1 rounded-full text-xs font-medium ${getDifficultyColor(lesson.difficulty)}`}>
                      {getDifficultyText(lesson.difficulty)}
                    </div>
                    <div className="flex items-center gap-1">
                      <Star className="w-4 h-4" />
                      {Math.round(lesson.difficulty * 5)}/5
                    </div>
                  </div>
                  
                  {lesson.tags && lesson.tags.length > 0 && (
                    <div className="flex items-center gap-2 mb-4">
                      <Tag className="w-4 h-4 text-gray-400" />
                      <div className="flex flex-wrap gap-1">
                        {lesson.tags.slice(0, 3).map((tag, i) => (
                          <span key={i} className="bg-gray-100 text-gray-600 text-xs px-2 py-1 rounded">
                            {tag}
                          </span>
                        ))}
                        {lesson.tags.length > 3 && (
                          <span className="text-gray-400 text-xs">+{lesson.tags.length - 3} more</span>
                        )}
                      </div>
                    </div>
                  )}
                  
                  {lesson.replacement_reason && (
                    <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 mb-4">
                      <p className="text-sm text-blue-800">
                        <strong>Why this lesson was added:</strong> {lesson.replacement_reason}
                      </p>
                    </div>
                  )}
                </div>
                
                <div className="flex flex-col gap-2 ml-4">
                  {lesson.status === 'upcoming' && (
                    <motion.button
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                      onClick={() => startLesson(lesson.lesson_id)}
                      className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-blue-700 transition-colors flex items-center gap-2"
                    >
                      Start Lesson
                      <ArrowRight className="w-4 h-4" />
                    </motion.button>
                  )}
                  
                  {lesson.status === 'in-progress' && (
                    <div className="text-center">
                      <div className="bg-yellow-100 text-yellow-800 px-3 py-1 rounded-full text-sm font-medium mb-2">
                        In Progress
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-yellow-500 h-2 rounded-full transition-all duration-300"
                          style={{ width: `${(lesson.progress || 0) * 100}%` }}
                        ></div>
                      </div>
                      <p className="text-xs text-gray-500 mt-1">
                        {Math.round((lesson.progress || 0) * 100)}% complete
                      </p>
                    </div>
                  )}
                  
                  {lesson.status === 'completed' && (
                    <div className="text-center">
                      <div className="bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm font-medium">
                        Completed
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
