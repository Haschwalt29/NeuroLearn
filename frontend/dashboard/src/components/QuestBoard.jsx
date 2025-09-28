import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Sword, Shield, Crown, Star, Clock, CheckCircle, Play, Plus } from 'lucide-react'

export default function QuestBoard({ userId, token, className = '' }) {
  const [quests, setQuests] = useState([])
  const [activeQuests, setActiveQuests] = useState([])
  const [loading, setLoading] = useState(true)
  const [selectedTab, setSelectedTab] = useState('available')

  useEffect(() => {
    fetchQuests()
  }, [userId, token])

  const fetchQuests = async () => {
    try {
      const [availableResponse, activeResponse] = await Promise.all([
        fetch('/api/quests/', {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }),
        fetch('/api/quests/active', {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        })
      ])
      
      if (availableResponse.ok && activeResponse.ok) {
        const availableData = await availableResponse.json()
        const activeData = await activeResponse.json()
        setQuests(availableData.quests)
        setActiveQuests(activeData.active_quests)
      }
    } catch (error) {
      console.error('Failed to fetch quests:', error)
    } finally {
      setLoading(false)
    }
  }

  const startQuest = async (questId) => {
    try {
      const response = await fetch('/api/quests/start', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ quest_id: questId })
      })
      
      if (response.ok) {
        fetchQuests() // Refresh data
      }
    } catch (error) {
      console.error('Failed to start quest:', error)
    }
  }

  const getThemeIcon = (theme) => {
    switch (theme) {
      case 'adventure': return Sword
      case 'mystery': return Shield
      case 'heroic': return Crown
      case 'scientific': return Star
      default: return Sword
    }
  }

  const getThemeColor = (theme) => {
    switch (theme) {
      case 'adventure': return 'from-green-500 to-blue-500'
      case 'mystery': return 'from-purple-500 to-indigo-500'
      case 'heroic': return 'from-yellow-500 to-orange-500'
      case 'scientific': return 'from-blue-500 to-cyan-500'
      default: return 'from-gray-500 to-gray-600'
    }
  }

  const getDifficultyColor = (difficulty) => {
    switch (difficulty) {
      case 'expert': return 'text-red-600 bg-red-100'
      case 'hard': return 'text-orange-600 bg-orange-100'
      case 'medium': return 'text-yellow-600 bg-yellow-100'
      case 'easy': return 'text-green-600 bg-green-100'
      default: return 'text-gray-600 bg-gray-100'
    }
  }

  const QuestCard = ({ quest, isActive = false }) => {
    const ThemeIcon = getThemeIcon(quest.story_theme)
    const themeColor = getThemeColor(quest.story_theme)

    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        whileHover={{ scale: 1.02 }}
        className={`bg-white border border-gray-200 rounded-lg p-4 hover:shadow-lg transition-shadow ${
          isActive ? 'ring-2 ring-blue-500' : ''
        }`}
      >
        {/* Quest Header */}
        <div className="flex items-start justify-between mb-3">
          <div className="flex items-center space-x-3">
            <div className={`w-10 h-10 rounded-full bg-gradient-to-r ${themeColor} flex items-center justify-center text-white`}>
              <ThemeIcon className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-semibold text-gray-900 text-sm">
                {quest.title}
              </h3>
              <div className="flex items-center space-x-2 mt-1">
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${getDifficultyColor(quest.difficulty)}`}>
                  {quest.difficulty}
                </span>
                <span className="text-xs text-gray-500 capitalize">
                  {quest.story_theme}
                </span>
              </div>
            </div>
          </div>
          
          <div className="text-right">
            <div className="text-sm font-bold text-gray-900">
              +{quest.xp_reward} XP
            </div>
            {quest.badge_reward && (
              <div className="text-xs text-gray-500">
                Badge Reward
              </div>
            )}
          </div>
        </div>

        {/* Quest Description */}
        <p className="text-sm text-gray-600 mb-3 line-clamp-2">
          {quest.description}
        </p>

        {/* Progress Bar (for active quests) */}
        {isActive && (
          <div className="mb-3">
            <div className="flex justify-between text-xs text-gray-600 mb-1">
              <span>Progress</span>
              <span>{Math.round(quest.progress_percentage)}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <motion.div
                className="bg-gradient-to-r from-blue-500 to-purple-500 h-2 rounded-full"
                initial={{ width: 0 }}
                animate={{ width: `${quest.progress_percentage}%` }}
                transition={{ duration: 1 }}
              />
            </div>
          </div>
        )}

        {/* Quest Tasks */}
        <div className="mb-3">
          <h4 className="text-xs font-semibold text-gray-700 mb-2">Tasks:</h4>
          <div className="space-y-1">
            {quest.required_tasks?.slice(0, 3).map((task, index) => (
              <div key={task.id} className="flex items-center space-x-2 text-xs">
                {isActive && quest.completed_tasks?.includes(task.id) ? (
                  <CheckCircle className="w-3 h-3 text-green-500" />
                ) : (
                  <div className="w-3 h-3 border border-gray-300 rounded-full" />
                )}
                <span className={`${isActive && quest.completed_tasks?.includes(task.id) ? 'line-through text-gray-500' : 'text-gray-700'}`}>
                  {task.title}
                </span>
              </div>
            ))}
            {quest.required_tasks?.length > 3 && (
              <div className="text-xs text-gray-500">
                +{quest.required_tasks.length - 3} more tasks
              </div>
            )}
          </div>
        </div>

        {/* Quest Footer */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-1 text-xs text-gray-500">
            <Clock className="w-3 h-3" />
            <span>{quest.estimated_duration} days</span>
          </div>
          
          {isActive ? (
            <div className="text-xs text-blue-600 font-medium">
              In Progress
            </div>
          ) : (
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => startQuest(quest.id)}
              className="flex items-center space-x-1 px-3 py-1 bg-blue-600 text-white rounded-lg text-xs font-medium hover:bg-blue-700 transition-colors"
            >
              <Play className="w-3 h-3" />
              <span>Start Quest</span>
            </motion.button>
          )}
        </div>
      </motion.div>
    )
  }

  if (loading) {
    return (
      <div className={`bg-white rounded-lg shadow-sm p-6 ${className}`}>
        <div className="animate-pulse">
          <div className="h-6 bg-gray-200 rounded w-1/3 mb-4"></div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="bg-gray-200 rounded-lg p-4 h-48"></div>
            ))}
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className={`bg-white rounded-lg shadow-sm ${className}`}>
      {/* Header */}
      <div className="p-6 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Quest Board</h2>
            <p className="text-gray-600">Embark on story-driven learning adventures</p>
          </div>
          
          <div className="flex items-center space-x-2">
            <div className="text-sm text-gray-600">
              {activeQuests.length} Active
            </div>
            <div className="w-2 h-2 bg-green-500 rounded-full"></div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="px-6 pt-4">
        <div className="flex space-x-1 bg-gray-100 rounded-lg p-1">
          <button
            onClick={() => setSelectedTab('available')}
            className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
              selectedTab === 'available'
                ? 'bg-white text-gray-900 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            Available ({quests.length})
          </button>
          <button
            onClick={() => setSelectedTab('active')}
            className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
              selectedTab === 'active'
                ? 'bg-white text-gray-900 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            Active ({activeQuests.length})
          </button>
        </div>
      </div>

      {/* Quest Grid */}
      <div className="p-6">
        <AnimatePresence mode="wait">
          {selectedTab === 'available' ? (
            <motion.div
              key="available"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              className="grid grid-cols-1 md:grid-cols-2 gap-4"
            >
              {quests.length > 0 ? (
                quests.map((quest) => (
                  <QuestCard key={quest.id} quest={quest} />
                ))
              ) : (
                <div className="col-span-2 text-center py-12">
                  <div className="w-16 h-16 mx-auto mb-4 bg-gray-100 rounded-full flex items-center justify-center">
                    <Sword className="w-8 h-8 text-gray-400" />
                  </div>
                  <h3 className="text-lg font-medium text-gray-900 mb-2">
                    No quests available
                  </h3>
                  <p className="text-gray-500">
                    Complete more activities to unlock new quests!
                  </p>
                </div>
              )}
            </motion.div>
          ) : (
            <motion.div
              key="active"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              className="grid grid-cols-1 md:grid-cols-2 gap-4"
            >
              {activeQuests.length > 0 ? (
                activeQuests.map((quest) => (
                  <QuestCard key={quest.id} quest={quest} isActive={true} />
                ))
              ) : (
                <div className="col-span-2 text-center py-12">
                  <div className="w-16 h-16 mx-auto mb-4 bg-gray-100 rounded-full flex items-center justify-center">
                    <Play className="w-8 h-8 text-gray-400" />
                  </div>
                  <h3 className="text-lg font-medium text-gray-900 mb-2">
                    No active quests
                  </h3>
                  <p className="text-gray-500">
                    Start a quest to begin your learning adventure!
                  </p>
                </div>
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  )
}
