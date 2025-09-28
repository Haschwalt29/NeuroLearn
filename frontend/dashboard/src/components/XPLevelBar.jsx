import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Star, Trophy, Zap, Crown } from 'lucide-react'

export default function XPLevelBar({ userId, token, className = '' }) {
  const [xpData, setXpData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [levelUpAnimation, setLevelUpAnimation] = useState(false)
  const [xpGainAnimation, setXpGainAnimation] = useState(null)

  useEffect(() => {
    fetchXPData()
  }, [userId, token])

  const fetchXPData = async () => {
    try {
      const response = await fetch('/api/gamification/status', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      })
      
      if (response.ok) {
        const data = await response.json()
        setXpData(data.xp_profile)
      }
    } catch (error) {
      console.error('Failed to fetch XP data:', error)
    } finally {
      setLoading(false)
    }
  }

  const getLevelIcon = (level) => {
    if (level >= 50) return Crown
    if (level >= 20) return Trophy
    if (level >= 10) return Star
    return Zap
  }

  const getLevelColor = (level) => {
    if (level >= 50) return 'from-purple-600 to-pink-600'
    if (level >= 20) return 'from-yellow-500 to-orange-500'
    if (level >= 10) return 'from-blue-500 to-purple-500'
    return 'from-green-500 to-blue-500'
  }

  const getLevelTitle = (level) => {
    if (level >= 50) return 'Legend'
    if (level >= 20) return 'Champion'
    if (level >= 10) return 'Expert'
    return 'Learner'
  }

  if (loading) {
    return (
      <div className={`bg-white rounded-lg shadow-sm p-4 ${className}`}>
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-1/3 mb-2"></div>
          <div className="h-3 bg-gray-200 rounded w-full"></div>
        </div>
      </div>
    )
  }

  if (!xpData) {
    return (
      <div className={`bg-white rounded-lg shadow-sm p-4 ${className}`}>
        <p className="text-gray-500">Failed to load XP data</p>
      </div>
    )
  }

  const LevelIcon = getLevelIcon(xpData.current_level)
  const levelColor = getLevelColor(xpData.current_level)
  const levelTitle = getLevelTitle(xpData.current_level)

  return (
    <div className={`bg-white rounded-lg shadow-sm p-4 ${className}`}>
      <AnimatePresence>
        {levelUpAnimation && (
          <motion.div
            initial={{ opacity: 0, scale: 0.5, y: -20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.5, y: -20 }}
            className="absolute inset-0 flex items-center justify-center bg-gradient-to-r from-yellow-400 to-orange-500 rounded-lg z-10"
          >
            <div className="text-center text-white">
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
              >
                <Trophy className="w-12 h-12 mx-auto mb-2" />
              </motion.div>
              <h3 className="text-xl font-bold">LEVEL UP!</h3>
              <p className="text-lg">Level {xpData.current_level}</p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      <AnimatePresence>
        {xpGainAnimation && (
          <motion.div
            initial={{ opacity: 0, y: 0 }}
            animate={{ opacity: 1, y: -20 }}
            exit={{ opacity: 0, y: -40 }}
            className="absolute top-2 right-2 bg-green-500 text-white px-2 py-1 rounded-full text-sm font-bold z-20"
          >
            +{xpGainAnimation} XP
          </motion.div>
        )}
      </AnimatePresence>

      <div className="relative">
        {/* Level and Title */}
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center space-x-3">
            <motion.div
              whileHover={{ scale: 1.1 }}
              className={`w-12 h-12 rounded-full bg-gradient-to-r ${levelColor} flex items-center justify-center text-white shadow-lg`}
            >
              <LevelIcon className="w-6 h-6" />
            </motion.div>
            <div>
              <h3 className="text-lg font-bold text-gray-900">
                Level {xpData.current_level}
              </h3>
              <p className="text-sm text-gray-600">{levelTitle}</p>
            </div>
          </div>
          
          <div className="text-right">
            <p className="text-sm text-gray-600">Total XP</p>
            <p className="text-lg font-bold text-gray-900">
              {xpData.total_xp.toLocaleString()}
            </p>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="mb-2">
          <div className="flex justify-between text-sm text-gray-600 mb-1">
            <span>{xpData.xp_in_current_level} XP</span>
            <span>{xpData.xp_to_next_level} XP to next level</span>
          </div>
          
          <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
            <motion.div
              className={`h-full bg-gradient-to-r ${levelColor} rounded-full`}
              initial={{ width: 0 }}
              animate={{ width: `${xpData.progress_percentage}%` }}
              transition={{ duration: 1, ease: "easeOut" }}
            />
          </div>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-3 gap-4 mt-4 pt-4 border-t border-gray-100">
          <div className="text-center">
            <p className="text-xs text-gray-500">Current Level</p>
            <p className="text-lg font-bold text-gray-900">{xpData.current_level}</p>
          </div>
          <div className="text-center">
            <p className="text-xs text-gray-500">XP to Next</p>
            <p className="text-lg font-bold text-gray-900">
              {xpData.xp_to_next_level - xpData.xp_in_current_level}
            </p>
          </div>
          <div className="text-center">
            <p className="text-xs text-gray-500">Progress</p>
            <p className="text-lg font-bold text-gray-900">
              {Math.round(xpData.progress_percentage)}%
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
