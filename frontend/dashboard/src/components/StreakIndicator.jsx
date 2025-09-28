import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Flame, Calendar, Target, Zap } from 'lucide-react'

export default function StreakIndicator({ userId, token, className = '' }) {
  const [streaks, setStreaks] = useState({})
  const [loading, setLoading] = useState(true)
  const [streakAnimation, setStreakAnimation] = useState(false)

  useEffect(() => {
    fetchStreakData()
  }, [userId, token])

  const fetchStreakData = async () => {
    try {
      const response = await fetch('/api/gamification/status', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      })
      
      if (response.ok) {
        const data = await response.json()
        setStreaks(data.streaks)
      }
    } catch (error) {
      console.error('Failed to fetch streak data:', error)
    } finally {
      setLoading(false)
    }
  }

  const getStreakIcon = (streakType) => {
    switch (streakType) {
      case 'daily_login': return Calendar
      case 'daily_lesson': return Target
      case 'quiz_streak': return Zap
      default: return Flame
    }
  }

  const getStreakColor = (streakType, currentStreak) => {
    if (currentStreak >= 30) return 'from-purple-600 to-pink-600'
    if (currentStreak >= 7) return 'from-orange-500 to-red-500'
    if (currentStreak >= 3) return 'from-yellow-500 to-orange-500'
    return 'from-gray-400 to-gray-500'
  }

  const getStreakTitle = (streakType) => {
    switch (streakType) {
      case 'daily_login': return 'Login Streak'
      case 'daily_lesson': return 'Learning Streak'
      case 'quiz_streak': return 'Quiz Streak'
      default: return 'Streak'
    }
  }

  const getStreakMilestone = (currentStreak) => {
    if (currentStreak >= 100) return 'Century Master'
    if (currentStreak >= 50) return 'Half Century'
    if (currentStreak >= 30) return 'Monthly Master'
    if (currentStreak >= 7) return 'Weekly Warrior'
    if (currentStreak >= 3) return 'Getting Started'
    return 'Beginner'
  }

  if (loading) {
    return (
      <div className={`bg-white rounded-lg shadow-sm p-4 ${className}`}>
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-1/2 mb-2"></div>
          <div className="h-8 bg-gray-200 rounded w-3/4"></div>
        </div>
      </div>
    )
  }

  const streakEntries = Object.entries(streaks)
  const totalStreakDays = streakEntries.reduce((sum, [_, streak]) => sum + streak.current, 0)

  return (
    <div className={`bg-white rounded-lg shadow-sm p-4 ${className}`}>
      <AnimatePresence>
        {streakAnimation && (
          <motion.div
            initial={{ opacity: 0, scale: 0.5 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.5 }}
            className="absolute inset-0 flex items-center justify-center bg-gradient-to-r from-orange-400 to-red-500 rounded-lg z-10"
          >
            <div className="text-center text-white">
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
              >
                <Flame className="w-12 h-12 mx-auto mb-2" />
              </motion.div>
              <h3 className="text-xl font-bold">STREAK!</h3>
              <p className="text-lg">{totalStreakDays} Days</p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      <div className="relative">
        {/* Header */}
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-gradient-to-r from-orange-500 to-red-500 rounded-full flex items-center justify-center text-white">
              <Flame className="w-4 h-4" />
            </div>
            <h3 className="text-lg font-bold text-gray-900">Streaks</h3>
          </div>
          
          <div className="text-right">
            <p className="text-sm text-gray-600">Total Days</p>
            <p className="text-xl font-bold text-gray-900">{totalStreakDays}</p>
          </div>
        </div>

        {/* Streak Cards */}
        <div className="space-y-3">
          {streakEntries.map(([streakType, streakData]) => {
            const StreakIcon = getStreakIcon(streakType)
            const streakColor = getStreakColor(streakType, streakData.current)
            const streakTitle = getStreakTitle(streakType)
            const milestone = getStreakMilestone(streakData.current)

            return (
              <motion.div
                key={streakType}
                whileHover={{ scale: 1.02 }}
                className={`bg-gradient-to-r ${streakColor} rounded-lg p-3 text-white`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <StreakIcon className="w-5 h-5" />
                    <div>
                      <h4 className="font-semibold text-sm">{streakTitle}</h4>
                      <p className="text-xs opacity-90">{milestone}</p>
                    </div>
                  </div>
                  
                  <div className="text-right">
                    <div className="text-xl font-bold">
                      {streakData.current}
                    </div>
                    <div className="text-xs opacity-90">
                      Best: {streakData.longest}
                    </div>
                  </div>
                </div>

                {/* Progress indicator for weekly milestones */}
                {streakData.current > 0 && (
                  <div className="mt-2">
                    <div className="w-full bg-white bg-opacity-20 rounded-full h-1">
                      <div 
                        className="bg-white h-1 rounded-full transition-all duration-300"
                        style={{ 
                          width: `${Math.min(100, (streakData.current % 7) * 14.28)}%` 
                        }}
                      />
                    </div>
                    <div className="text-xs opacity-90 mt-1">
                      {streakData.current % 7 === 0 ? 'Weekly milestone!' : `${7 - (streakData.current % 7)} days to next milestone`}
                    </div>
                  </div>
                )}

                {/* Frozen indicator */}
                {streakData.frozen && (
                  <div className="mt-2 text-xs bg-white bg-opacity-20 rounded px-2 py-1 inline-block">
                    🧊 Streak Protected
                  </div>
                )}
              </motion.div>
            )
          })}
        </div>

        {/* Streak Tips */}
        <div className="mt-4 p-3 bg-gray-50 rounded-lg">
          <h4 className="text-sm font-semibold text-gray-900 mb-2">Streak Tips</h4>
          <ul className="text-xs text-gray-600 space-y-1">
            <li>• Login daily to maintain your login streak</li>
            <li>• Complete at least one lesson per day</li>
            <li>• Take quizzes regularly to build quiz streaks</li>
            <li>• Use streak freeze items to protect your progress</li>
          </ul>
        </div>
      </div>
    </div>
  )
}
