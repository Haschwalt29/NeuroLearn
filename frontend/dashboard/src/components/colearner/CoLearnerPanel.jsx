import React, { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import axios from 'axios'
import CoLearnerAvatar from './CoLearnerAvatar'
import { useAuth } from '../../contexts/AuthContext'
import { useSocket } from '../../contexts/SocketContext'

export default function CoLearnerPanel({ isOpen, onClose }) {
  const { token } = useAuth()
  const { on } = useSocket()
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [profile, setProfile] = useState(null)
  const [showLevelUp, setShowLevelUp] = useState(false)
  const [levelUpData, setLevelUpData] = useState(null)

  useEffect(() => {
    if (!isOpen) return
    const fetchState = async () => {
      const res = await axios.get('/api/colearner/state', { headers: { Authorization: `Bearer ${token}` } })
      setProfile(res.data.profile)
    }
    fetchState()
  }, [isOpen, token])

  useEffect(() => {
    const messageHandler = (payload) => {
      setMessages((m) => [...m, { from: 'co', text: payload?.text || '' }])
    }
    
    const xpHandler = (payload) => {
      if (profile) {
        setProfile(prev => ({ ...prev, xp: payload.xp, level: payload.level }))
      }
    }
    
    const levelUpHandler = (payload) => {
      setLevelUpData(payload)
      setShowLevelUp(true)
      setTimeout(() => setShowLevelUp(false), 5000)
    }
    
    on('colearner_message', messageHandler)
    on('colearner_xp_update', xpHandler)
    on('colearner_level_up', levelUpHandler)
    
    return () => {}
  }, [on, profile])

  const sendMessage = async () => {
    const text = input.trim()
    if (!text) return
    setMessages((m) => [...m, { from: 'me', text }])
    setInput('')
    const res = await axios.post('/api/colearner/message', { message: text }, { headers: { Authorization: `Bearer ${token}` } })
    if (res.data?.text) {
      setMessages((m) => [...m, { from: 'co', text: res.data.text }])
    }
  }

  if (!isOpen) return null
  return (
    <div className="fixed inset-0 bg-black/40 z-50 flex items-center justify-center p-4">
      <div className="bg-white w-full max-w-2xl rounded-lg shadow-lg overflow-hidden">
        <div className="p-4 border-b flex items-center justify-between">
          <div className="flex items-center gap-2">
            <CoLearnerAvatar mood="happy" />
            <div>
              <div className="font-semibold flex items-center gap-2">
                {profile?.persona_config?.name || 'Co-Learner'}
                {profile?.level && (
                  <span className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded-full">
                    Level {profile.level}
                  </span>
                )}
              </div>
              <div className="text-xs text-gray-500 flex items-center gap-2">
                <span>{profile?.persona_config?.tone || 'friendly'}</span>
                {profile?.traits && profile.traits.length > 0 && (
                  <span className="text-blue-600">
                    {profile.traits.join(', ')}
                  </span>
                )}
              </div>
              {profile?.xp !== undefined && (
                <div className="mt-1">
                  <div className="flex items-center gap-2 text-xs text-gray-600">
                    <span>XP: {profile.xp}</span>
                    <div className="flex-1 bg-gray-200 rounded-full h-1.5">
                      <div 
                        className="bg-blue-500 h-1.5 rounded-full transition-all duration-300"
                        style={{ width: `${((profile.xp % 100) / 100) * 100}%` }}
                      ></div>
                    </div>
                    <span>{100 - (profile.xp % 100)} to next level</span>
                  </div>
                </div>
              )}
            </div>
          </div>
          <button onClick={onClose} className="text-gray-500 hover:text-gray-700">✕</button>
        </div>
        <div className="p-4 h-[420px] overflow-y-auto space-y-2 bg-gray-50">
          {messages.map((m, i) => (
            <div key={i} className={`max-w-[80%] ${m.from==='me' ? 'ml-auto text-right' : ''}`}>
              <div className={`inline-block px-3 py-2 rounded-lg ${m.from==='me' ? 'bg-blue-600 text-white' : 'bg-white border'}`}>{m.text}</div>
            </div>
          ))}
        </div>
        <div className="p-3 border-t flex items-center gap-2">
          <input value={input} onChange={(e) => setInput(e.target.value)} placeholder="Ask or say anything…" className="flex-1 border rounded px-3 py-2" />
          <motion.button whileHover={{ scale: 1.03 }} whileTap={{ scale: 0.97 }} onClick={sendMessage} className="px-4 py-2 bg-blue-600 text-white rounded-lg">Send</motion.button>
        </div>
      </div>
      
      {/* Level Up Celebration */}
      {showLevelUp && levelUpData && (
        <div className="fixed inset-0 bg-black/50 z-60 flex items-center justify-center">
          <motion.div
            initial={{ scale: 0, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0, opacity: 0 }}
            className="bg-gradient-to-r from-yellow-400 to-orange-500 text-white p-8 rounded-2xl shadow-2xl text-center max-w-md mx-4"
          >
            <div className="text-6xl mb-4">🎉</div>
            <h3 className="text-2xl font-bold mb-2">Level Up!</h3>
            <p className="text-lg mb-4">
              {profile?.persona_config?.name || 'Co-Learner'} reached Level {levelUpData.level}!
            </p>
            {levelUpData.new_traits && levelUpData.new_traits.length > 0 && (
              <div className="mb-4">
                <p className="text-sm mb-2">New traits unlocked:</p>
                <div className="flex flex-wrap gap-2 justify-center">
                  {levelUpData.new_traits.map((trait, i) => (
                    <span key={i} className="bg-white/20 px-3 py-1 rounded-full text-sm">
                      {trait}
                    </span>
                  ))}
                </div>
              </div>
            )}
            <button
              onClick={() => setShowLevelUp(false)}
              className="bg-white/20 hover:bg-white/30 px-6 py-2 rounded-lg transition-colors"
            >
              Awesome!
            </button>
          </motion.div>
        </div>
      )}
    </div>
  )
}


