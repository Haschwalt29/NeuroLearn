import React from 'react'
import { motion } from 'framer-motion'
import { Trophy, Star, Target, Zap, Heart, Brain } from 'lucide-react'

export default function Achievements() {
  const achievements = [
    {
      id: 1,
      title: 'First Steps',
      description: 'Complete your first lesson',
      icon: Target,
      earned: true,
      date: '2024-01-15',
      color: 'green'
    },
    {
      id: 2,
      title: 'Streak Master',
      description: 'Study for 7 days in a row',
      icon: Zap,
      earned: true,
      date: '2024-01-20',
      color: 'orange'
    },
    {
      id: 3,
      title: 'Happy Learner',
      description: 'Stay positive for 30 minutes',
      icon: Heart,
      earned: true,
      date: '2024-01-22',
      color: 'pink'
    },
    {
      id: 4,
      title: 'Quick Learner',
      description: 'Complete 10 lessons in one day',
      icon: Brain,
      earned: false,
      progress: 7,
      total: 10,
      color: 'blue'
    },
    {
      id: 5,
      title: 'Emotion Master',
      description: 'Detect 100 emotions',
      icon: Star,
      earned: false,
      progress: 23,
      total: 100,
      color: 'purple'
    },
    {
      id: 6,
      title: 'Champion',
      description: 'Earn 10 achievements',
      icon: Trophy,
      earned: false,
      progress: 3,
      total: 10,
      color: 'yellow'
    }
  ]

  const getColorClasses = (color, earned) => {
    const colors = {
      green: earned ? 'text-green-600 bg-green-100' : 'text-green-400 bg-green-50',
      orange: earned ? 'text-orange-600 bg-orange-100' : 'text-orange-400 bg-orange-50',
      pink: earned ? 'text-pink-600 bg-pink-100' : 'text-pink-400 bg-pink-50',
      blue: earned ? 'text-blue-600 bg-blue-100' : 'text-blue-400 bg-blue-50',
      purple: earned ? 'text-purple-600 bg-purple-100' : 'text-purple-400 bg-purple-50',
      yellow: earned ? 'text-yellow-600 bg-yellow-100' : 'text-yellow-400 bg-yellow-50'
    }
    return colors[color] || colors.blue
  }

  const earnedAchievements = achievements.filter(a => a.earned)
  const pendingAchievements = achievements.filter(a => !a.earned)

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="card"
    >
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold text-gray-900">Achievements</h3>
        <div className="flex items-center space-x-2">
          <Trophy className="w-5 h-5 text-gray-400" />
          <span className="text-sm text-gray-600">{earnedAchievements.length}/{achievements.length}</span>
        </div>
      </div>

      <div className="space-y-4">
        {/* Earned Achievements */}
        {earnedAchievements.map((achievement, index) => (
          <motion.div
            key={achievement.id}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.1 }}
            className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg"
          >
            <div className={`p-2 rounded-lg ${getColorClasses(achievement.color, true)}`}>
              <achievement.icon className="w-5 h-5" />
            </div>
            <div className="flex-1">
              <h4 className="font-medium text-gray-900">{achievement.title}</h4>
              <p className="text-sm text-gray-600">{achievement.description}</p>
              <p className="text-xs text-gray-500">Earned on {achievement.date}</p>
            </div>
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: index * 0.1 + 0.2 }}
              className="text-yellow-500"
            >
              <Star className="w-5 h-5 fill-current" />
            </motion.div>
          </motion.div>
        ))}

        {/* Pending Achievements */}
        {pendingAchievements.map((achievement, index) => (
          <motion.div
            key={achievement.id}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: (earnedAchievements.length + index) * 0.1 }}
            className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg opacity-75"
          >
            <div className={`p-2 rounded-lg ${getColorClasses(achievement.color, false)}`}>
              <achievement.icon className="w-5 h-5" />
            </div>
            <div className="flex-1">
              <h4 className="font-medium text-gray-700">{achievement.title}</h4>
              <p className="text-sm text-gray-500">{achievement.description}</p>
              <div className="mt-2">
                <div className="flex items-center justify-between text-xs text-gray-500 mb-1">
                  <span>Progress</span>
                  <span>{achievement.progress}/{achievement.total}</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-1">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${(achievement.progress / achievement.total) * 100}%` }}
                    transition={{ delay: (earnedAchievements.length + index) * 0.1 + 0.3 }}
                    className="h-1 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full"
                  />
                </div>
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      <div className="mt-6 p-4 bg-gradient-to-r from-yellow-50 to-orange-50 rounded-lg">
        <div className="flex items-center space-x-3">
          <Trophy className="w-5 h-5 text-yellow-600" />
          <div>
            <h4 className="font-medium text-gray-900">Achievement Progress</h4>
            <p className="text-sm text-gray-600">
              You're {achievements.length - earnedAchievements.length} achievements away from becoming a champion!
            </p>
          </div>
        </div>
      </div>
    </motion.div>
  )
}
