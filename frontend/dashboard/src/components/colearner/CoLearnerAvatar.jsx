import React from 'react'
import { motion } from 'framer-motion'

export default function CoLearnerAvatar({ mood = 'neutral' }) {
  const color = mood === 'happy' ? '#10b981' : mood === 'frustrated' ? '#ef4444' : '#3b82f6'
  return (
    <motion.div className="w-12 h-12 rounded-full flex items-center justify-center"
      style={{ background: color }}
      animate={{ scale: [1, 1.05, 1] }} transition={{ repeat: Infinity, duration: 2 }}>
      <span className="text-white text-sm">AI</span>
    </motion.div>
  )
}


