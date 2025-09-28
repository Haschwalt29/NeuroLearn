import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Users, TrendingUp, Eye, BarChart3 } from 'lucide-react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts'

export default function AdminDashboard() {
  const [students, setStudents] = useState([])
  const [emotionData, setEmotionData] = useState([])
  const [stats, setStats] = useState({
    totalStudents: 0,
    activeStudents: 0,
    avgEmotionScore: 0,
    totalLessons: 0
  })

  useEffect(() => {
    // Mock data - replace with actual API calls
    setStudents([
      { id: 1, name: 'Alice Johnson', email: 'alice@example.com', progress: 75, lastActive: '2 hours ago', emotion: 'happy' },
      { id: 2, name: 'Bob Smith', email: 'bob@example.com', progress: 60, lastActive: '1 day ago', emotion: 'neutral' },
      { id: 3, name: 'Carol Davis', email: 'carol@example.com', progress: 90, lastActive: '30 minutes ago', emotion: 'excited' },
      { id: 4, name: 'David Wilson', email: 'david@example.com', progress: 45, lastActive: '3 days ago', emotion: 'confused' }
    ])

    setEmotionData([
      { time: '9:00', happy: 12, sad: 3, neutral: 8, confused: 2 },
      { time: '10:00', happy: 15, sad: 2, neutral: 6, confused: 1 },
      { time: '11:00', happy: 18, sad: 1, neutral: 5, confused: 0 },
      { time: '12:00', happy: 20, sad: 0, neutral: 4, confused: 1 },
      { time: '13:00', happy: 16, sad: 2, neutral: 7, confused: 2 },
      { time: '14:00', happy: 14, sad: 3, neutral: 8, confused: 1 }
    ])

    setStats({
      totalStudents: 4,
      activeStudents: 3,
      avgEmotionScore: 7.2,
      totalLessons: 156
    })
  }, [])

  const getEmotionColor = (emotion) => {
    const colors = {
      happy: 'text-green-600 bg-green-100',
      excited: 'text-yellow-600 bg-yellow-100',
      neutral: 'text-gray-600 bg-gray-100',
      confused: 'text-red-600 bg-red-100',
      sad: 'text-blue-600 bg-blue-100'
    }
    return colors[emotion] || colors.neutral
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-8"
        >
          {/* Header */}
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Admin Dashboard</h1>
            <p className="text-gray-600 mt-2">Monitor student progress and learning analytics</p>
          </div>

          {/* Stats Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              className="card"
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Total Students</p>
                  <p className="text-2xl font-bold text-gray-900">{stats.totalStudents}</p>
                </div>
                <Users className="w-8 h-8 text-blue-600" />
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="card"
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Active Students</p>
                  <p className="text-2xl font-bold text-gray-900">{stats.activeStudents}</p>
                </div>
                <Eye className="w-8 h-8 text-green-600" />
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              className="card"
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Avg Emotion Score</p>
                  <p className="text-2xl font-bold text-gray-900">{stats.avgEmotionScore}/10</p>
                </div>
                <TrendingUp className="w-8 h-8 text-purple-600" />
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
              className="card"
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Total Lessons</p>
                  <p className="text-2xl font-bold text-gray-900">{stats.totalLessons}</p>
                </div>
                <BarChart3 className="w-8 h-8 text-orange-600" />
              </div>
            </motion.div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Emotion Timeline Chart */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5 }}
              className="card"
            >
              <h3 className="text-lg font-semibold text-gray-900 mb-6">Student Emotions Over Time</h3>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={emotionData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                    <XAxis dataKey="time" stroke="#666" />
                    <YAxis stroke="#666" />
                    <Tooltip />
                    <Line type="monotone" dataKey="happy" stroke="#10b981" strokeWidth={2} />
                    <Line type="monotone" dataKey="sad" stroke="#3b82f6" strokeWidth={2} />
                    <Line type="monotone" dataKey="neutral" stroke="#6b7280" strokeWidth={2} />
                    <Line type="monotone" dataKey="confused" stroke="#ef4444" strokeWidth={2} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </motion.div>

            {/* Emotion Distribution */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.6 }}
              className="card"
            >
              <h3 className="text-lg font-semibold text-gray-900 mb-6">Emotion Distribution</h3>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={[
                    { emotion: 'Happy', count: 20 },
                    { emotion: 'Neutral', count: 15 },
                    { emotion: 'Confused', count: 5 },
                    { emotion: 'Sad', count: 3 }
                  ]}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                    <XAxis dataKey="emotion" stroke="#666" />
                    <YAxis stroke="#666" />
                    <Tooltip />
                    <Bar dataKey="count" fill="#3b82f6" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </motion.div>
          </div>

          {/* Student List */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.7 }}
            className="card"
          >
            <h3 className="text-lg font-semibold text-gray-900 mb-6">Student Progress</h3>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Student
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Progress
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Current Emotion
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Last Active
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {students.map((student) => (
                    <motion.tr
                      key={student.id}
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      transition={{ delay: 0.1 * student.id }}
                      className="hover:bg-gray-50"
                    >
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div>
                          <div className="text-sm font-medium text-gray-900">{student.name}</div>
                          <div className="text-sm text-gray-500">{student.email}</div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <div className="w-16 bg-gray-200 rounded-full h-2 mr-2">
                            <div
                              className="bg-blue-600 h-2 rounded-full"
                              style={{ width: `${student.progress}%` }}
                            />
                          </div>
                          <span className="text-sm text-gray-900">{student.progress}%</span>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getEmotionColor(student.emotion)}`}>
                          {student.emotion}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {student.lastActive}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        <button className="text-blue-600 hover:text-blue-900 mr-3">
                          View Details
                        </button>
                        <button className="text-green-600 hover:text-green-900">
                          Message
                        </button>
                      </td>
                    </motion.tr>
                  ))}
                </tbody>
              </table>
            </div>
          </motion.div>
        </motion.div>
      </div>
    </div>
  )
}
