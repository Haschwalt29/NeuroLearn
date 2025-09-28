import React, { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import axios from 'axios'
import CoLearnerAvatar from './CoLearnerAvatar'
import { useAuth } from '../../contexts/AuthContext'
import { useSocket } from '../../contexts/SocketContext'

export default function CoLearnerWidget({ onOpen }) {
  const { token } = useAuth()
  const { on } = useSocket()
  const [lastMsg, setLastMsg] = useState('')

  useEffect(() => {
    const handler = (payload) => setLastMsg(payload?.text || '')
    on('colearner_message', handler)
    return () => {}
  }, [on])

  return (
    <motion.button onClick={onOpen}
      className="fixed bottom-6 right-6 bg-white shadow-lg rounded-full px-3 py-2 flex items-center gap-2 border"
      whileHover={{ scale: 1.03 }} whileTap={{ scale: 0.97 }}>
      <CoLearnerAvatar />
      <div className="text-xs text-gray-600 max-w-[180px] truncate">{lastMsg || 'Study with your AI co-learner'}</div>
    </motion.button>
  )
}


