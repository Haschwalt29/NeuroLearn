import React, { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import axios from 'axios'
import { useAuth } from '../../contexts/AuthContext'
import { useSocket } from '../../contexts/SocketContext'
import { Bell, BookOpen, RefreshCw, CheckCircle, Sparkles, ArrowRight } from 'lucide-react'

export default function CurriculumUpdates() {
  const { token } = useAuth()
  const { on } = useSocket()
  const [updates, setUpdates] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchUpdates()
  }, [token])

  useEffect(() => {
    const handler = (payload) => {
      if (payload.updates) {
        // Refresh updates when curriculum changes
        fetchUpdates()
      }
    }
    on('curriculum_update', handler)
    return () => {}
  }, [on])

  const fetchUpdates = async () => {
    try {
      setLoading(true)
      const response = await axios.get('/api/curriculum/updates', {
        headers: { Authorization: `Bearer ${token}` }
      })
      setUpdates(response.data.updates || [])
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const markAsRead = async (updateId) => {
    try {
      await axios.post(`/api/curriculum/updates/${updateId}/read`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      })
      setUpdates(prev => prev.map(update => 
        update.id === updateId ? { ...update, is_read: true } : update
      ))
    } catch (err) {
      console.error('Failed to mark update as read:', err)
    }
  }

  const getUpdateIcon = (type) => {
    switch (type) {
      case 'new_lesson':
        return <BookOpen className="w-5 h-5 text-green-600" />
      case 'replaced_lesson':
        return <RefreshCw className="w-5 h-5 text-blue-600" />
      case 'updated_path':
        return <ArrowRight className="w-5 h-5 text-purple-600" />
      default:
        return <Bell className="w-5 h-5 text-gray-600" />
    }
  }

  const getUpdateColor = (type) => {
    switch (type) {
      case 'new_lesson':
        return 'bg-green-50 border-green-200'
      case 'replaced_lesson':
        return 'bg-blue-50 border-blue-200'
      case 'updated_path':
        return 'bg-purple-50 border-purple-200'
      default:
        return 'bg-gray-50 border-gray-200'
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
        Error loading updates: {error}
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
        <Bell className="w-6 h-6 text-orange-600" />
        <h2 className="text-2xl font-bold text-gray-800">Curriculum Updates</h2>
        <span className="bg-orange-100 text-orange-800 text-sm px-2 py-1 rounded-full">
          {updates.filter(u => !u.is_read).length} unread
        </span>
      </div>

      {updates.length === 0 ? (
        <div className="text-center py-12 text-gray-500">
          <Bell className="w-16 h-16 mx-auto mb-4 text-gray-300" />
          <p className="text-lg">No curriculum updates yet</p>
          <p className="text-sm">Updates will appear here when your learning path changes</p>
        </div>
      ) : (
        <div className="space-y-4">
          {updates.map((update, index) => (
            <motion.div
              key={update.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
              className={`bg-white rounded-lg border-2 p-4 ${getUpdateColor(update.type)} ${
                !update.is_read ? 'ring-2 ring-blue-200' : ''
              }`}
            >
              <div className="flex items-start gap-3">
                <div className="flex-shrink-0 mt-1">
                  {getUpdateIcon(update.type)}
                </div>
                
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <h3 className="font-semibold text-gray-800">{update.message}</h3>
                    {!update.is_read && (
                      <span className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded-full flex items-center gap-1">
                        <Sparkles className="w-3 h-3" />
                        New
                      </span>
                    )}
                  </div>
                  
                  <p className="text-sm text-gray-600 mb-2">
                    {new Date(update.created_at).toLocaleDateString('en-US', {
                      year: 'numeric',
                      month: 'long',
                      day: 'numeric',
                      hour: '2-digit',
                      minute: '2-digit'
                    })}
                  </p>
                  
                  {update.lesson_title && (
                    <div className="bg-white/50 rounded-lg p-3 mb-3">
                      <p className="text-sm font-medium text-gray-700">
                        <BookOpen className="w-4 h-4 inline mr-1" />
                        {update.lesson_title}
                      </p>
                    </div>
                  )}
                  
                  {update.metadata && Object.keys(update.metadata).length > 0 && (
                    <div className="text-xs text-gray-500">
                      {update.metadata.reason && (
                        <span>Reason: {update.metadata.reason}</span>
                      )}
                    </div>
                  )}
                </div>
                
                <div className="flex-shrink-0">
                  {!update.is_read && (
                    <button
                      onClick={() => markAsRead(update.id)}
                      className="text-blue-600 hover:text-blue-800 text-sm font-medium flex items-center gap-1"
                    >
                      <CheckCircle className="w-4 h-4" />
                      Mark as read
                    </button>
                  )}
                  {update.is_read && (
                    <div className="text-green-600 text-sm flex items-center gap-1">
                      <CheckCircle className="w-4 h-4" />
                      Read
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
