import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { X, Star, Trophy, Crown, Zap, Shield, Sword, Target } from 'lucide-react'

export default function BadgeModal({ isOpen, onClose, userId, token }) {
  const [badges, setBadges] = useState([])
  const [loading, setLoading] = useState(true)
  const [selectedCategory, setSelectedCategory] = useState('all')
  const [selectedRarity, setSelectedRarity] = useState('all')

  useEffect(() => {
    if (isOpen) {
      fetchBadges()
    }
  }, [isOpen, userId, token])

  const fetchBadges = async () => {
    try {
      const response = await fetch('/api/gamification/badges', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      })
      
      if (response.ok) {
        const data = await response.json()
        setBadges(data.badges)
      }
    } catch (error) {
      console.error('Failed to fetch badges:', error)
    } finally {
      setLoading(false)
    }
  }

  const getRarityIcon = (rarity) => {
    switch (rarity) {
      case 'legendary': return Crown
      case 'epic': return Trophy
      case 'rare': return Star
      default: return Zap
    }
  }

  const getRarityColor = (rarity) => {
    switch (rarity) {
      case 'legendary': return 'from-purple-600 to-pink-600'
      case 'epic': return 'from-yellow-500 to-orange-500'
      case 'rare': return 'from-blue-500 to-purple-500'
      default: return 'from-green-500 to-blue-500'
    }
  }

  const getCategoryIcon = (category) => {
    switch (category) {
      case 'achievement': return Target
      case 'streak': return Zap
      case 'mastery': return Trophy
      case 'level': return Star
      case 'emotion': return Shield
      case 'quest': return Sword
      case 'special': return Crown
      default: return Star
    }
  }

  const filteredBadges = badges.filter(badge => {
    const categoryMatch = selectedCategory === 'all' || badge.category === selectedCategory
    const rarityMatch = selectedRarity === 'all' || badge.rarity === selectedRarity
    return categoryMatch && rarityMatch
  })

  const categories = ['all', 'achievement', 'streak', 'mastery', 'level', 'emotion', 'quest', 'special']
  const rarities = ['all', 'common', 'rare', 'epic', 'legendary']

  if (!isOpen) return null

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50"
        onClick={onClose}
      >
        <motion.div
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.9, opacity: 0 }}
          className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-hidden"
          onClick={(e) => e.stopPropagation()}
        >
          {/* Header */}
          <div className="p-6 border-b border-gray-200">
            <div className="flex justify-between items-center">
              <div>
                <h2 className="text-2xl font-bold text-gray-900">Achievement Badges</h2>
                <p className="text-gray-600">Your earned achievements and milestones</p>
              </div>
              <button
                onClick={onClose}
                className="text-gray-400 hover:text-gray-600 transition-colors"
              >
                <X className="w-6 h-6" />
              </button>
            </div>
          </div>

          {/* Filters */}
          <div className="p-4 border-b border-gray-200 bg-gray-50">
            <div className="flex flex-wrap gap-4">
              {/* Category Filter */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Category
                </label>
                <select
                  value={selectedCategory}
                  onChange={(e) => setSelectedCategory(e.target.value)}
                  className="px-3 py-1 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  {categories.map(category => (
                    <option key={category} value={category}>
                      {category.charAt(0).toUpperCase() + category.slice(1)}
                    </option>
                  ))}
                </select>
              </div>

              {/* Rarity Filter */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Rarity
                </label>
                <select
                  value={selectedRarity}
                  onChange={(e) => setSelectedRarity(e.target.value)}
                  className="px-3 py-1 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  {rarities.map(rarity => (
                    <option key={rarity} value={rarity}>
                      {rarity.charAt(0).toUpperCase() + rarity.slice(1)}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          </div>

          {/* Badges Grid */}
          <div className="p-6 overflow-y-auto max-h-[60vh]">
            {loading ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {[...Array(6)].map((_, i) => (
                  <div key={i} className="animate-pulse">
                    <div className="bg-gray-200 rounded-lg p-4 h-32"></div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {filteredBadges.map((badge, index) => {
                  const RarityIcon = getRarityIcon(badge.rarity)
                  const CategoryIcon = getCategoryIcon(badge.category)
                  const rarityColor = getRarityColor(badge.rarity)

                  return (
                    <motion.div
                      key={badge.id}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: index * 0.1 }}
                      className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-lg transition-shadow"
                    >
                      {/* Badge Header */}
                      <div className="flex items-start justify-between mb-3">
                        <div className="flex items-center space-x-2">
                          <div className={`w-8 h-8 rounded-full bg-gradient-to-r ${rarityColor} flex items-center justify-center text-white text-lg`}>
                            {badge.icon}
                          </div>
                          <div>
                            <h3 className="font-semibold text-gray-900 text-sm">
                              {badge.name}
                            </h3>
                            <div className="flex items-center space-x-1">
                              <RarityIcon className="w-3 h-3 text-gray-400" />
                              <span className="text-xs text-gray-500 capitalize">
                                {badge.rarity}
                              </span>
                            </div>
                          </div>
                        </div>
                        
                        <div className="flex items-center space-x-1 text-xs text-gray-500">
                          <CategoryIcon className="w-3 h-3" />
                          <span className="capitalize">{badge.category}</span>
                        </div>
                      </div>

                      {/* Badge Description */}
                      <p className="text-sm text-gray-600 mb-3 line-clamp-2">
                        {badge.description}
                      </p>

                      {/* Badge Footer */}
                      <div className="flex items-center justify-between">
                        <div className="text-xs text-gray-500">
                          Earned: {new Date(badge.earned_at).toLocaleDateString()}
                        </div>
                        {badge.xp_reward > 0 && (
                          <div className="text-xs font-semibold text-green-600">
                            +{badge.xp_reward} XP
                          </div>
                        )}
                      </div>
                    </motion.div>
                  )
                })}
              </div>
            )}

            {!loading && filteredBadges.length === 0 && (
              <div className="text-center py-12">
                <div className="w-16 h-16 mx-auto mb-4 bg-gray-100 rounded-full flex items-center justify-center">
                  <Trophy className="w-8 h-8 text-gray-400" />
                </div>
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  No badges found
                </h3>
                <p className="text-gray-500">
                  Try adjusting your filters or complete more activities to earn badges!
                </p>
              </div>
            )}
          </div>

          {/* Footer */}
          <div className="p-6 border-t border-gray-200 bg-gray-50">
            <div className="flex justify-between items-center">
              <div className="text-sm text-gray-600">
                Showing {filteredBadges.length} of {badges.length} badges
              </div>
              <button
                onClick={onClose}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                Close
              </button>
            </div>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  )
}
