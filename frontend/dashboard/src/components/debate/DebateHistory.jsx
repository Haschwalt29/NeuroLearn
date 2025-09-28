import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import axios from 'axios'
import { useAuth } from '../../contexts/AuthContext'
import { MessageCircle, Clock, Target, Award, Play, Eye, Trash2 } from 'lucide-react'

export default function DebateHistory() {
  const { token } = useAuth()
  const [debates, setDebates] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [selectedDebate, setSelectedDebate] = useState(null)
  const [showResults, setShowResults] = useState(false)

  useEffect(() => {
    fetchDebateHistory()
  }, [token])

  const fetchDebateHistory = async () => {
    try {
      setLoading(true)
      const response = await axios.get('/api/debate/history?limit=20', {
        headers: { Authorization: `Bearer ${token}` }
      })
      setDebates(response.data.data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'active': return 'text-blue-600 bg-blue-100'
      case 'ended': return 'text-green-600 bg-green-100'
      case 'paused': return 'text-yellow-600 bg-yellow-100'
      default: return 'text-gray-600 bg-gray-100'
    }
  }

  const getScoreColor = (score) => {
    if (score >= 8) return 'text-green-600'
    if (score >= 6) return 'text-yellow-600'
    return 'text-red-600'
  }

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const viewResults = async (debateId) => {
    try {
      const response = await axios.get(`/api/debate/session/${debateId}`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      setSelectedDebate(response.data.data)
      setShowResults(true)
    } catch (err) {
      console.error('Failed to fetch debate details:', err)
    }
  }

  const deleteDebate = async (debateId) => {
    if (!window.confirm('Are you sure you want to delete this debate?')) return
    
    try {
      await axios.delete(`/api/debate/session/${debateId}`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      fetchDebateHistory() // Refresh the list
    } catch (err) {
      console.error('Failed to delete debate:', err)
      alert('Failed to delete debate. Please try again.')
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
        Error loading debate history: {error}
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <MessageCircle className="w-6 h-6 text-blue-600" />
        <h2 className="text-2xl font-bold text-gray-800">Debate History</h2>
        <span className="bg-blue-100 text-blue-800 text-sm px-2 py-1 rounded-full">
          {debates.length} debates
        </span>
      </div>

      {debates.length === 0 ? (
        <div className="text-center py-12 text-gray-500">
          <MessageCircle className="w-16 h-16 mx-auto mb-4 text-gray-300" />
          <p className="text-lg">No debates yet</p>
          <p className="text-sm">Start your first debate to see it here</p>
        </div>
      ) : (
        <div className="grid gap-4">
          {debates.map((debate, index) => (
            <motion.div
              key={debate.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="bg-white rounded-lg border border-gray-200 p-6 hover:shadow-md transition-shadow"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <h3 className="text-lg font-semibold text-gray-800">{debate.topic}</h3>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(debate.status)}`}>
                      {debate.status.toUpperCase()}
                    </span>
                  </div>
                  
                  <div className="flex items-center gap-4 text-sm text-gray-500 mb-3">
                    <div className="flex items-center gap-1">
                      <Target className="w-4 h-4" />
                      You: {debate.learner_stance.toUpperCase()}
                    </div>
                    <div className="flex items-center gap-1">
                      <MessageCircle className="w-4 h-4" />
                      {debate.total_turns} turns
                    </div>
                    <div className="flex items-center gap-1">
                      <Clock className="w-4 h-4" />
                      {formatDate(debate.created_at)}
                    </div>
                    {debate.stance_switches > 0 && (
                      <div className="flex items-center gap-1 text-purple-600">
                        <Award className="w-4 h-4" />
                        {debate.stance_switches} switches
                      </div>
                    )}
                  </div>
                  
                  {debate.status === 'ended' && debate.learner_score > 0 && (
                    <div className="flex items-center gap-4 text-sm">
                      <div className="flex items-center gap-1">
                        <span className="text-gray-600">Your Score:</span>
                        <span className={`font-semibold ${getScoreColor(debate.learner_score)}`}>
                          {Math.round(debate.learner_score)}/10
                        </span>
                      </div>
                      <div className="flex items-center gap-1">
                        <span className="text-gray-600">Debate Quality:</span>
                        <span className={`font-semibold ${getScoreColor(debate.debate_quality)}`}>
                          {Math.round(debate.debate_quality)}/10
                        </span>
                      </div>
                    </div>
                  )}
                </div>
                
                <div className="flex items-center gap-2 ml-4">
                  {debate.status === 'ended' ? (
                    <motion.button
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                      onClick={() => viewResults(debate.id)}
                      className="px-3 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 flex items-center gap-1"
                    >
                      <Eye className="w-4 h-4" />
                      View Results
                    </motion.button>
                  ) : (
                    <motion.button
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                      onClick={() => viewResults(debate.id)}
                      className="px-3 py-2 bg-green-600 text-white rounded-lg text-sm font-medium hover:bg-green-700 flex items-center gap-1"
                    >
                      <Play className="w-4 h-4" />
                      Continue
                    </motion.button>
                  )}
                  
                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={() => deleteDebate(debate.id)}
                    className="px-3 py-2 text-gray-500 hover:text-red-600 rounded-lg text-sm"
                  >
                    <Trash2 className="w-4 h-4" />
                  </motion.button>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      )}

      {/* Results Modal */}
      {showResults && selectedDebate && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.9 }}
            className="bg-white w-full max-w-4xl h-[80vh] rounded-lg shadow-lg overflow-hidden flex flex-col"
          >
            <div className="p-4 border-b flex items-center justify-between">
              <h3 className="text-lg font-semibold text-gray-800">Debate Results</h3>
              <button
                onClick={() => setShowResults(false)}
                className="text-gray-500 hover:text-gray-700 text-xl"
              >
                ✕
              </button>
            </div>
            <div className="flex-1 overflow-y-auto p-4">
              <DebateResults 
                sessionId={selectedDebate.session.id} 
                onClose={() => setShowResults(false)} 
              />
            </div>
          </motion.div>
        </div>
      )}
    </div>
  )
}
