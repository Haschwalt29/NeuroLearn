import React from 'react'
import { motion } from 'framer-motion'
import { Clock, BookOpen, Flame, Trophy } from 'lucide-react'

export default function StatsCards({ stats }) {
  const cards = [
    {
      title: 'Study Time',
      value: `${stats.totalStudyTime}m`,
      icon: Clock,
      color: 'blue',
      description: 'Total time spent learning'
    },
    {
      title: 'Lessons Completed',
      value: stats.lessonsCompleted,
      icon: BookOpen,
      color: 'green',
      description: 'Lessons finished this week'
    },
    {
      title: 'Current Streak',
      value: `${stats.currentStreak} days`,
      icon: Flame,
      color: 'orange',
      description: 'Days in a row'
    },
    {
      title: 'Achievements',
      value: stats.achievements,
      icon: Trophy,
      color: 'purple',
      description: 'Badges earned'
    }
  ]

  const getColorClasses = (color) => {
    const colors = {
      blue: 'text-blue-600 bg-blue-100',
      green: 'text-green-600 bg-green-100',
      orange: 'text-orange-600 bg-orange-100',
      purple: 'text-purple-600 bg-purple-100'
    }
    return colors[color] || colors.blue
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {cards.map((card, index) => (
        <motion.div
          key={card.title}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: index * 0.1 }}
          whileHover={{ scale: 1.05 }}
          className="card hover:shadow-md transition-shadow"
        >
          <div className="flex items-center justify-between mb-4">
            <div className={`p-3 rounded-lg ${getColorClasses(card.color)}`}>
              <card.icon className="w-6 h-6" />
            </div>
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: index * 0.1 + 0.2 }}
              className="text-2xl font-bold text-gray-900"
            >
              {card.value}
            </motion.div>
          </div>
          
          <div>
            <h3 className="text-sm font-medium text-gray-900 mb-1">
              {card.title}
            </h3>
            <p className="text-xs text-gray-500">
              {card.description}
            </p>
          </div>
        </motion.div>
      ))}
    </div>
  )
}
