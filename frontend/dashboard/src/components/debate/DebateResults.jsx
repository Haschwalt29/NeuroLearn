import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import axios from 'axios'
import { useAuth } from '../../contexts/AuthContext'
import { Award, Target, Brain, MessageCircle, RotateCcw, Clock, TrendingUp, AlertCircle } from 'lucide-react'

export default function DebateResults({ sessionId, onClose }) {
  const { token } = useAuth()
  const [session, setSession] = useState(null)
  const [turns, setTurns] = useState([])
  const [scores, setScores] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    if (sessionId) {
      fetchSessionDetails()
    }
  }, [sessionId])

  const fetchSessionDetails = async () => {
    try {
      setLoading(true)
      const response = await axios.get(`/api/debate/session/${sessionId}`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      
      const data = response.data.data
      setSession(data.session)
      setTurns(data.turns)
      setScores(data.scores)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const getScoreColor = (score) => {
    if (score >= 8) return 'text-green-600 bg-green-100'
    if (score >= 6) return 'text-yellow-600 bg-yellow-100'
    return 'text-red-600 bg-red-100'
  }

  const getScoreLabel = (score) => {
    if (score >= 8) return 'Excellent'
    if (score >= 6) return 'Good'
    if (score >= 4) return 'Fair'
    return 'Needs Improvement'
  }

  const getOverallGrade = (score) => {
    if (score >= 8.5) return { grade: 'A+', color: 'text-green-600' }
    if (score >= 8) return { grade: 'A', color: 'text-green-600' }
    if (score >= 7.5) return { grade: 'B+', color: 'text-blue-600' }
    if (score >= 7) return { grade: 'B', color: 'text-blue-600' }
    if (score >= 6.5) return { grade: 'C+', color: 'text-yellow-600' }
    if (score >= 6) return { grade: 'C', color: 'text-yellow-600' }
    if (score >= 5) return { grade: 'D', color: 'text-orange-600' }
    return { grade: 'F', color: 'text-red-600' }
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
        Error loading debate results: {error}
      </div>
    )
  }

  if (!session) {
    return (
      <div className="text-center py-8 text-gray-500">
        No debate session found
      </div>
    )
  }

  const learnerScores = scores.filter(s => s.scorer_type === 'system')
  const avgScores = learnerScores.length > 0 ? {
    logic: learnerScores.reduce((sum, s) => sum + s.logic_score, 0) / learnerScores.length,
    clarity: learnerScores.reduce((sum, s) => sum + s.clarity_score, 0) / learnerScores.length,
    persuasion: learnerScores.reduce((sum, s) => sum + s.persuasiveness_score, 0) / learnerScores.length,
    evidence: learnerScores.reduce((sum, s) => sum + s.evidence_quality, 0) / learnerScores.length,
    critical_thinking: learnerScores.reduce((sum, s) => sum + s.critical_thinking, 0) / learnerScores.length,
    respectfulness: learnerScores.reduce((sum, s) => sum + s.respectfulness, 0) / learnerScores.length,
    overall: learnerScores.reduce((sum, s) => sum + s.overall_score, 0) / learnerScores.length
  } : {}

  const overallGrade = getOverallGrade(avgScores.overall || 0)

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-6"
    >
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg p-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-gray-800 mb-2">Debate Results</h2>
            <p className="text-gray-600">{session.topic}</p>
            <div className="flex items-center gap-4 mt-2 text-sm text-gray-500">
              <span>Total Turns: {session.total_turns}</span>
              <span>•</span>
              <span>Stance Switches: {session.stance_switches}</span>
              <span>•</span>
              <span>Duration: {Math.round((new Date(session.ended_at) - new Date(session.created_at)) / 60000)} min</span>
            </div>
          </div>
          <div className="text-right">
            <div className={`text-4xl font-bold ${overallGrade.color}`}>
              {overallGrade.grade}
            </div>
            <div className="text-sm text-gray-500">Overall Grade</div>
          </div>
        </div>
      </div>

      {/* Performance Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <div className="bg-white p-4 rounded-lg border border-gray-200">
          <div className="flex items-center gap-3 mb-2">
            <Brain className="w-5 h-5 text-blue-600" />
            <span className="font-medium text-gray-800">Logic & Reasoning</span>
          </div>
          <div className={`text-2xl font-bold ${getScoreColor(avgScores.logic || 0).split(' ')[0]}`}>
            {Math.round(avgScores.logic || 0)}/10
          </div>
          <div className="text-sm text-gray-500">{getScoreLabel(avgScores.logic || 0)}</div>
        </div>

        <div className="bg-white p-4 rounded-lg border border-gray-200">
          <div className="flex items-center gap-3 mb-2">
            <MessageCircle className="w-5 h-5 text-green-600" />
            <span className="font-medium text-gray-800">Clarity & Communication</span>
          </div>
          <div className={`text-2xl font-bold ${getScoreColor(avgScores.clarity || 0).split(' ')[0]}`}>
            {Math.round(avgScores.clarity || 0)}/10
          </div>
          <div className="text-sm text-gray-500">{getScoreLabel(avgScores.clarity || 0)}</div>
        </div>

        <div className="bg-white p-4 rounded-lg border border-gray-200">
          <div className="flex items-center gap-3 mb-2">
            <Target className="w-5 h-5 text-purple-600" />
            <span className="font-medium text-gray-800">Persuasiveness</span>
          </div>
          <div className={`text-2xl font-bold ${getScoreColor(avgScores.persuasion || 0).split(' ')[0]}`}>
            {Math.round(avgScores.persuasion || 0)}/10
          </div>
          <div className="text-sm text-gray-500">{getScoreLabel(avgScores.persuasion || 0)}</div>
        </div>

        <div className="bg-white p-4 rounded-lg border border-gray-200">
          <div className="flex items-center gap-3 mb-2">
            <Award className="w-5 h-5 text-yellow-600" />
            <span className="font-medium text-gray-800">Evidence Quality</span>
          </div>
          <div className={`text-2xl font-bold ${getScoreColor(avgScores.evidence || 0).split(' ')[0]}`}>
            {Math.round(avgScores.evidence || 0)}/10
          </div>
          <div className="text-sm text-gray-500">{getScoreLabel(avgScores.evidence || 0)}</div>
        </div>

        <div className="bg-white p-4 rounded-lg border border-gray-200">
          <div className="flex items-center gap-3 mb-2">
            <TrendingUp className="w-5 h-5 text-indigo-600" />
            <span className="font-medium text-gray-800">Critical Thinking</span>
          </div>
          <div className={`text-2xl font-bold ${getScoreColor(avgScores.critical_thinking || 0).split(' ')[0]}`}>
            {Math.round(avgScores.critical_thinking || 0)}/10
          </div>
          <div className="text-sm text-gray-500">{getScoreLabel(avgScores.critical_thinking || 0)}</div>
        </div>

        <div className="bg-white p-4 rounded-lg border border-gray-200">
          <div className="flex items-center gap-3 mb-2">
            <Clock className="w-5 h-5 text-pink-600" />
            <span className="font-medium text-gray-800">Respectfulness</span>
          </div>
          <div className={`text-2xl font-bold ${getScoreColor(avgScores.respectfulness || 0).split(' ')[0]}`}>
            {Math.round(avgScores.respectfulness || 0)}/10
          </div>
          <div className="text-sm text-gray-500">{getScoreLabel(avgScores.respectfulness || 0)}</div>
        </div>
      </div>

      {/* Detailed Analysis */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Strengths */}
        <div className="bg-white p-6 rounded-lg border border-gray-200">
          <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-green-600" />
            Your Strengths
          </h3>
          {learnerScores.length > 0 && learnerScores[0].strengths && learnerScores[0].strengths.length > 0 ? (
            <div className="space-y-2">
              {learnerScores[0].strengths.map((strength, index) => (
                <div key={index} className="flex items-center gap-2 text-green-700">
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                  <span className="capitalize">{strength.replace('_', ' ')}</span>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500 text-sm">No specific strengths identified yet. Keep practicing!</p>
          )}
        </div>

        {/* Improvement Areas */}
        <div className="bg-white p-6 rounded-lg border border-gray-200">
          <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
            <AlertCircle className="w-5 h-5 text-orange-600" />
            Areas for Improvement
          </h3>
          {learnerScores.length > 0 && learnerScores[0].improvement_areas && learnerScores[0].improvement_areas.length > 0 ? (
            <div className="space-y-2">
              {learnerScores[0].improvement_areas.map((area, index) => (
                <div key={index} className="flex items-center gap-2 text-orange-700">
                  <div className="w-2 h-2 bg-orange-500 rounded-full"></div>
                  <span className="capitalize">{area.replace('_', ' ')}</span>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500 text-sm">Great job! No major improvement areas identified.</p>
          )}
        </div>
      </div>

      {/* Debate Transcript */}
      <div className="bg-white p-6 rounded-lg border border-gray-200">
        <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
          <MessageCircle className="w-5 h-5 text-blue-600" />
          Debate Transcript
        </h3>
        <div className="space-y-4 max-h-96 overflow-y-auto">
          {turns.map((turn, index) => (
            <div key={index} className={`p-4 rounded-lg ${
              turn.speaker === 'learner' 
                ? 'bg-blue-50 border-l-4 border-blue-500' 
                : 'bg-gray-50 border-l-4 border-gray-400'
            }`}>
              <div className="flex items-center gap-2 mb-2">
                <span className={`font-medium ${
                  turn.speaker === 'learner' ? 'text-blue-700' : 'text-gray-700'
                }`}>
                  {turn.speaker === 'learner' ? 'You' : 'AI'}
                </span>
                {turn.turn_type === 'stance_switch' && (
                  <span className="text-xs bg-purple-100 text-purple-700 px-2 py-1 rounded-full flex items-center gap-1">
                    <RotateCcw className="w-3 h-3" />
                    Stance Switch
                  </span>
                )}
                <span className="text-xs text-gray-500">
                  Turn {turn.turn_number}
                </span>
              </div>
              <p className="text-gray-800 whitespace-pre-wrap">{turn.message}</p>
              {turn.word_count && (
                <div className="text-xs text-gray-500 mt-2">
                  {turn.word_count} words
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex justify-end gap-3">
        <button
          onClick={onClose}
          className="px-6 py-2 text-gray-600 hover:text-gray-800"
        >
          Close
        </button>
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={() => window.print()}
          className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          Print Results
        </motion.button>
      </div>
    </motion.div>
  )
}
