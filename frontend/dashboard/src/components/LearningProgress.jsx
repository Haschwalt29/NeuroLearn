import React from 'react'
import { motion } from 'framer-motion'
import { Target, TrendingUp, Award } from 'lucide-react'

export default function LearningProgress() {
  const progressData = [
    { skill: 'Machine Learning', progress: 75, level: 'Intermediate' },
    { skill: 'Python Programming', progress: 90, level: 'Advanced' },
    { skill: 'Data Analysis', progress: 60, level: 'Intermediate' },
    { skill: 'Neural Networks', progress: 45, level: 'Beginner' }
  ]

  const getLevelColor = (level) => {
    switch (level) {
      case 'Beginner': return 'text-green-600 bg-green-100'
      case 'Intermediate': return 'text-yellow-600 bg-yellow-100'
      case 'Advanced': return 'text-red-600 bg-red-100'
      default: return 'text-gray-600 bg-gray-100'
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="card"
    >
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold text-gray-900">Learning Progress</h3>
        <div className="flex items-center space-x-2">
          <TrendingUp className="w-5 h-5 text-gray-400" />
          <span className="text-sm text-gray-600">Skills</span>
        </div>
      </div>

      <div className="space-y-6">
        {progressData.map((item, index) => (
          <motion.div
            key={item.skill}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.1 }}
            className="space-y-2"
          >
            <div className="flex items-center justify-between">
              <h4 className="font-medium text-gray-900">{item.skill}</h4>
              <div className="flex items-center space-x-2">
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${getLevelColor(item.level)}`}>
                  {item.level}
                </span>
                <span className="text-sm text-gray-600">{item.progress}%</span>
              </div>
            </div>
            
            <div className="w-full bg-gray-200 rounded-full h-2">
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${item.progress}%` }}
                transition={{ delay: index * 0.1 + 0.3, duration: 0.8 }}
                className="h-2 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full"
              />
            </div>
          </motion.div>
        ))}
      </div>

      <div className="mt-6 p-4 bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg">
        <div className="flex items-center space-x-3">
          <Award className="w-5 h-5 text-blue-600" />
          <div>
            <h4 className="font-medium text-gray-900">Next Milestone</h4>
            <p className="text-sm text-gray-600">
              Complete 3 more lessons to unlock the "Data Scientist" badge
            </p>
          </div>
        </div>
      </div>
    </motion.div>
  )
}
