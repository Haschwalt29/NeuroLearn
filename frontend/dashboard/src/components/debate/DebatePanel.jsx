import React, { useState, useEffect, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import axios from 'axios'
import { useAuth } from '../../contexts/AuthContext'
import { useSocket } from '../../contexts/SocketContext'
import { MessageCircle, RotateCcw, Square, Play, Brain, Target, Zap, Award } from 'lucide-react'

export default function DebatePanel({ isOpen, onClose, sessionId = null }) {
  const { token } = useAuth()
  const { on } = useSocket()
  const [session, setSession] = useState(null)
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [topics, setTopics] = useState([])
  const [showTopicSelection, setShowTopicSelection] = useState(!sessionId)
  const [selectedTopic, setSelectedTopic] = useState('')
  const [selectedStance, setSelectedStance] = useState('neutral')
  const [selectedDifficulty, setSelectedDifficulty] = useState('intermediate')
  const [scores, setScores] = useState({})
  const [aiStance, setAiStance] = useState('con')
  const [stanceSwitches, setStanceSwitches] = useState(0)
  
  const messagesEndRef = useRef(null)
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    if (isOpen) {
      if (sessionId) {
        fetchSession()
      } else {
        fetchTopics()
      }
    }
  }, [isOpen, sessionId])

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  useEffect(() => {
    const handlers = {
      debate_turn: (payload) => {
        if (payload.session_id === session?.id) {
          setMessages(prev => [
            ...prev,
            { speaker: 'learner', message: payload.learner_message, scores: payload.learner_scores },
            { speaker: 'ai', message: payload.ai_message, scores: payload.learner_scores }
          ])
          setScores(payload.learner_scores)
        }
      },
      debate_stance_switch: (payload) => {
        if (payload.session_id === session?.id) {
          setAiStance(payload.new_stance)
          setStanceSwitches(payload.total_switches)
          setMessages(prev => [
            ...prev,
            { speaker: 'ai', message: payload.switch_message, isStanceSwitch: true }
          ])
        }
      },
      debate_ended: (payload) => {
        if (payload.session_id === session?.id) {
          setSession(prev => ({ ...prev, status: 'ended' }))
          setScores(payload.final_scores)
        }
      }
    }

    Object.entries(handlers).forEach(([event, handler]) => {
      on(event, handler)
    })

    return () => {}
  }, [on, session?.id])

  const fetchSession = async () => {
    try {
      const response = await axios.get(`/api/debate/session/${sessionId}`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      const data = response.data.data
      setSession(data.session)
      setMessages(data.turns.map(turn => ({
        speaker: turn.speaker,
        message: turn.message,
        turnNumber: turn.turn_number,
        stance: turn.stance,
        isStanceSwitch: turn.turn_type === 'stance_switch'
      })))
      setAiStance(data.session.ai_stance)
      setStanceSwitches(data.session.stance_switches)
    } catch (error) {
      console.error('Failed to fetch session:', error)
    }
  }

  const fetchTopics = async () => {
    try {
      const response = await axios.get(`/api/debate/topics?difficulty=${selectedDifficulty}`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      setTopics(response.data.data)
    } catch (error) {
      console.error('Failed to fetch topics:', error)
    }
  }

  const startDebate = async () => {
    if (!selectedTopic) return
    
    try {
      setLoading(true)
      const response = await axios.post('/api/debate/start', {
        topic: selectedTopic,
        stance: selectedStance,
        difficulty: selectedDifficulty
      }, {
        headers: { Authorization: `Bearer ${token}` }
      })
      
      const data = response.data.data
      setSession({
        id: data.session_id,
        topic: data.topic,
        learner_stance: data.learner_stance,
        ai_stance: data.ai_stance,
        status: 'active'
      })
      setAiStance(data.ai_stance)
      setMessages([{ speaker: 'ai', message: data.opening_message, isOpening: true }])
      setShowTopicSelection(false)
    } catch (error) {
      console.error('Failed to start debate:', error)
    } finally {
      setLoading(false)
    }
  }

  const sendMessage = async () => {
    if (!input.trim() || !session) return
    
    try {
      setLoading(true)
      const response = await axios.post('/api/debate/reply', {
        session_id: session.id,
        learner_message: input
      }, {
        headers: { Authorization: `Bearer ${token}` }
      })
      
      const data = response.data.data
      setMessages(prev => [
        ...prev,
        { speaker: 'learner', message: input, scores: data.learner_scores },
        { speaker: 'ai', message: data.ai_message, scores: data.learner_scores }
      ])
      setScores(data.learner_scores)
      setInput('')
    } catch (error) {
      console.error('Failed to send message:', error)
      // Show user-friendly error message
      if (error.response?.data?.error) {
        alert(`Error: ${error.response.data.error}`)
      } else {
        alert('Failed to send message. Please try again.')
      }
    } finally {
      setLoading(false)
    }
  }

  const switchStance = async () => {
    if (!session) return
    
    try {
      setLoading(true)
      await axios.post('/api/debate/switch', {
        session_id: session.id
      }, {
        headers: { Authorization: `Bearer ${token}` }
      })
    } catch (error) {
      console.error('Failed to switch stance:', error)
    } finally {
      setLoading(false)
    }
  }

  const endDebate = async () => {
    if (!session) return
    
    try {
      setLoading(true)
      const response = await axios.post('/api/debate/end', {
        session_id: session.id
      }, {
        headers: { Authorization: `Bearer ${token}` }
      })
      
      const data = response.data.data
      setSession(prev => ({ ...prev, status: 'ended' }))
      setScores(data.final_scores)
    } catch (error) {
      console.error('Failed to end debate:', error)
    } finally {
      setLoading(false)
    }
  }

  const getStanceColor = (stance) => {
    switch (stance) {
      case 'pro': return 'text-green-600 bg-green-100'
      case 'con': return 'text-red-600 bg-red-100'
      case 'for': return 'text-green-600 bg-green-100'
      case 'against': return 'text-red-600 bg-red-100'
      default: return 'text-gray-600 bg-gray-100'
    }
  }

  const getStanceText = (stance) => {
    switch (stance) {
      case 'pro': return 'PRO'
      case 'con': return 'CON'
      case 'for': return 'FOR'
      case 'against': return 'AGAINST'
      default: return 'NEUTRAL'
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black/40 z-50 flex items-center justify-center p-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.9 }}
        className="bg-white w-full max-w-4xl h-[80vh] rounded-lg shadow-lg overflow-hidden flex flex-col"
      >
        {/* Header */}
        <div className="p-4 border-b bg-gradient-to-r from-blue-50 to-purple-50">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <MessageCircle className="w-6 h-6 text-blue-600" />
              <div>
                <h2 className="text-xl font-bold text-gray-800">Socratic Debate</h2>
                {session && (
                  <div className="flex items-center gap-2 text-sm text-gray-600">
                    <span>Topic: {session.topic}</span>
                    <span className="text-gray-400">•</span>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStanceColor(session.learner_stance)}`}>
                      You: {getStanceText(session.learner_stance)}
                    </span>
                    <span className="text-gray-400">•</span>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStanceColor(aiStance)}`}>
                      AI: {getStanceText(aiStance)}
                    </span>
                    {stanceSwitches > 0 && (
                      <>
                        <span className="text-gray-400">•</span>
                        <span className="text-purple-600 text-xs">
                          {stanceSwitches} stance switch{stanceSwitches !== 1 ? 'es' : ''}
                        </span>
                      </>
                    )}
                  </div>
                )}
              </div>
            </div>
            <button onClick={onClose} className="text-gray-500 hover:text-gray-700 text-xl">✕</button>
          </div>
        </div>

        {/* Topic Selection */}
        {showTopicSelection && (
          <div className="p-6 space-y-4">
            <h3 className="text-lg font-semibold text-gray-800">Choose Your Debate Topic</h3>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Difficulty Level</label>
                <select
                  value={selectedDifficulty}
                  onChange={(e) => {
                    setSelectedDifficulty(e.target.value)
                    fetchTopics()
                  }}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2"
                >
                  <option value="beginner">Beginner</option>
                  <option value="intermediate">Intermediate</option>
                  <option value="advanced">Advanced</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Your Stance</label>
                <select
                  value={selectedStance}
                  onChange={(e) => setSelectedStance(e.target.value)}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2"
                >
                  <option value="pro">Pro / For</option>
                  <option value="con">Con / Against</option>
                  <option value="neutral">Neutral</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Select Topic</label>
                <div className="space-y-2 max-h-60 overflow-y-auto">
                  {topics.map((topic, index) => (
                    <button
                      key={index}
                      onClick={() => setSelectedTopic(topic.topic)}
                      className={`w-full text-left p-3 rounded-lg border transition-colors ${
                        selectedTopic === topic.topic
                          ? 'border-blue-500 bg-blue-50'
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                    >
                      <div className="font-medium text-gray-800">{topic.topic}</div>
                      <div className="text-sm text-gray-500 capitalize">{topic.category}</div>
                    </button>
                  ))}
                </div>
              </div>
            </div>

            <div className="flex justify-end gap-3">
              <button
                onClick={onClose}
                className="px-4 py-2 text-gray-600 hover:text-gray-800"
              >
                Cancel
              </button>
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={startDebate}
                disabled={!selectedTopic || loading}
                className="px-6 py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
              >
                {loading ? (
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                ) : (
                  <Play className="w-4 h-4" />
                )}
                Start Debate
              </motion.button>
            </div>
          </div>
        )}

        {/* Debate Interface */}
        {session && !showTopicSelection && (
          <>
            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50">
              <AnimatePresence>
                {messages.map((message, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -20 }}
                    className={`flex ${message.speaker === 'learner' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div className={`max-w-[80%] ${message.speaker === 'learner' ? 'order-2' : 'order-1'}`}>
                      <div className={`inline-block px-4 py-3 rounded-lg ${
                        message.speaker === 'learner'
                          ? 'bg-blue-600 text-white'
                          : message.isStanceSwitch
                          ? 'bg-purple-100 text-purple-800 border-2 border-purple-300'
                          : 'bg-white text-gray-800 border border-gray-200'
                      }`}>
                        {message.isStanceSwitch && (
                          <div className="flex items-center gap-2 mb-2 text-sm font-medium">
                            <RotateCcw className="w-4 h-4" />
                            AI Switched Stance
                          </div>
                        )}
                        <div className="whitespace-pre-wrap">{message.message}</div>
                        {message.scores && message.speaker === 'learner' && (
                          <div className="mt-2 pt-2 border-t border-white/20 text-xs">
                            <div className="flex gap-4">
                              <span>Logic: {Math.round(message.scores.logic_score)}/10</span>
                              <span>Clarity: {Math.round(message.scores.clarity_score)}/10</span>
                              <span>Persuasion: {Math.round(message.scores.persuasiveness_score)}/10</span>
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  </motion.div>
                ))}
              </AnimatePresence>
              <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            {session.status === 'active' && (
              <div className="p-4 border-t bg-white">
                <div className="flex gap-2">
                  <input
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && !loading && sendMessage()}
                    placeholder="Type your argument..."
                    className="flex-1 border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    disabled={loading}
                  />
                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={sendMessage}
                    disabled={!input.trim() || loading}
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {loading ? (
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                    ) : (
                      'Send'
                    )}
                  </motion.button>
                </div>
              </div>
            )}

            {/* Controls */}
            <div className="p-4 border-t bg-gray-50 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={switchStance}
                  disabled={loading || session.status !== 'active'}
                  className="px-3 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 text-sm"
                >
                  <RotateCcw className="w-4 h-4" />
                  Switch AI Stance
                </motion.button>
                
                {session.status === 'active' && (
                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={endDebate}
                    disabled={loading}
                    className="px-3 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 text-sm"
                  >
                    <Square className="w-4 h-4" />
                    End Debate
                  </motion.button>
                )}
              </div>

              {session.status === 'ended' && (
                <div className="text-sm text-gray-600">
                  Debate completed! Check your results.
                </div>
              )}
            </div>
          </>
        )}
      </motion.div>
    </div>
  )
}
