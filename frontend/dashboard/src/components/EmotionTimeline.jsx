import React from 'react'
import { motion } from 'framer-motion'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { useEmotion } from '../contexts/EmotionContext'
import { TrendingUp, Activity } from 'lucide-react'

export default function EmotionTimeline() {
  const { emotions, getEmotionColor } = useEmotion()

  // Process emotions for chart
  const chartData = emotions.slice(0, 20).reverse().map((emotion, index) => ({
    time: emotion.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    emotion: emotion.emotion,
    confidence: emotion.confidence,
    index
  }))

  const getEmotionValue = (emotion) => {
    const values = {
      happy: 100,
      surprise: 80,
      neutral: 50,
      sad: 20,
      fear: 10,
      angry: 5,
      disgust: 0
    }
    return values[emotion] || 50
  }

  const processedData = chartData.map(item => ({
    ...item,
    value: getEmotionValue(item.emotion)
  }))

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload
      return (
        <div className="bg-white p-3 rounded-lg shadow-lg border">
          <p className="font-medium">{`Time: ${label}`}</p>
          <p className="text-sm" style={{ color: getEmotionColor(data.emotion) }}>
            {`Emotion: ${data.emotion}`}
          </p>
          <p className="text-sm text-gray-600">
            {`Confidence: ${Math.round(data.confidence)}%`}
          </p>
        </div>
      )
    }
    return null
  }

  const getEmotionStats = () => {
    if (emotions.length === 0) return null

    const emotionCounts = emotions.reduce((acc, emotion) => {
      acc[emotion.emotion] = (acc[emotion.emotion] || 0) + 1
      return acc
    }, {})

    const mostCommon = Object.entries(emotionCounts)
      .sort(([,a], [,b]) => b - a)[0]

    const avgConfidence = emotions.reduce((sum, emotion) => sum + emotion.confidence, 0) / emotions.length

    return {
      mostCommon: mostCommon ? mostCommon[0] : 'neutral',
      count: mostCommon ? mostCommon[1] : 0,
      avgConfidence: Math.round(avgConfidence)
    }
  }

  const stats = getEmotionStats()

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="card"
    >
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">Emotion Timeline</h3>
        <Activity className="w-5 h-5 text-gray-400" />
      </div>

      {emotions.length > 0 ? (
        <div className="space-y-4">
          {/* Stats */}
          {stats && (
            <div className="grid grid-cols-2 gap-4 mb-4">
              <div className="text-center p-3 bg-gray-50 rounded-lg">
                <p className="text-sm text-gray-600">Most Common</p>
                <p 
                  className="font-semibold capitalize"
                  style={{ color: getEmotionColor(stats.mostCommon) }}
                >
                  {stats.mostCommon}
                </p>
                <p className="text-xs text-gray-500">{stats.count} times</p>
              </div>
              <div className="text-center p-3 bg-gray-50 rounded-lg">
                <p className="text-sm text-gray-600">Avg Confidence</p>
                <p className="font-semibold text-gray-900">{stats.avgConfidence}%</p>
                <p className="text-xs text-gray-500">Detection accuracy</p>
              </div>
            </div>
          )}

          {/* Chart */}
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={processedData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis 
                  dataKey="time" 
                  stroke="#666"
                  fontSize={12}
                  tickLine={false}
                  axisLine={false}
                />
                <YAxis 
                  stroke="#666"
                  fontSize={12}
                  tickLine={false}
                  axisLine={false}
                  domain={[0, 100]}
                  tickFormatter={(value) => `${value}%`}
                />
                <Tooltip content={<CustomTooltip />} />
                <Line
                  type="monotone"
                  dataKey="value"
                  stroke="#3b82f6"
                  strokeWidth={2}
                  dot={false}
                  activeDot={{ r: 4, fill: '#3b82f6' }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* Recent Emotions */}
          <div className="space-y-2">
            <h4 className="text-sm font-medium text-gray-700">Recent Emotions</h4>
            <div className="space-y-1 max-h-32 overflow-y-auto">
              {emotions.slice(0, 5).map((emotion, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="flex items-center justify-between p-2 bg-gray-50 rounded-lg"
                >
                  <div className="flex items-center space-x-2">
                    <div
                      className="w-3 h-3 rounded-full"
                      style={{ backgroundColor: getEmotionColor(emotion.emotion) }}
                    />
                    <span className="text-sm font-medium capitalize">
                      {emotion.emotion}
                    </span>
                  </div>
                  <div className="text-xs text-gray-500">
                    {emotion.timestamp.toLocaleTimeString([], { 
                      hour: '2-digit', 
                      minute: '2-digit' 
                    })}
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        </div>
      ) : (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="text-center py-8"
        >
          <TrendingUp className="w-12 h-12 text-gray-300 mx-auto mb-4" />
          <p className="text-gray-500 mb-2">No emotion data yet</p>
          <p className="text-sm text-gray-400">
            Start emotion detection to see your mood timeline
          </p>
        </motion.div>
      )}
    </motion.div>
  )
}
