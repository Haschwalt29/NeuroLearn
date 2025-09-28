import React from 'react'
import { motion } from 'framer-motion'
import { useEmotion } from '../contexts/EmotionContext'
import { Camera, Shield, Bell, Palette, Users } from 'lucide-react'
import CoLearnerSettings from '../components/colearner/CoLearnerSettings'

export default function Settings() {
  const { emotionOptIn, toggleEmotionOptIn, isCapturing, startCapture, stopCapture } = useEmotion()

  const handleEmotionToggle = async (enabled) => {
    await toggleEmotionOptIn(enabled)
    if (enabled && !isCapturing) {
      await startCapture()
    } else if (!enabled && isCapturing) {
      stopCapture()
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-8"
        >
          {/* Header */}
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Settings</h1>
            <p className="text-gray-600 mt-2">Manage your AI Tutor preferences and privacy settings</p>
          </div>

          {/* Privacy Settings */}
          <div className="card">
            <div className="flex items-center space-x-3 mb-6">
              <Shield className="w-6 h-6 text-blue-600" />
              <h2 className="text-xl font-semibold text-gray-900">Privacy & Data</h2>
            </div>

            <div className="space-y-6">
              <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <div className="flex items-center space-x-3">
                  <Camera className="w-5 h-5 text-gray-600" />
                  <div>
                    <h3 className="font-medium text-gray-900">Emotion Detection</h3>
                    <p className="text-sm text-gray-600">
                      Allow AI Tutor to analyze your facial expressions for personalized learning
                    </p>
                  </div>
                </div>
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={() => handleEmotionToggle(!emotionOptIn)}
                  className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                    emotionOptIn ? 'bg-blue-600' : 'bg-gray-200'
                  }`}
                >
                  <motion.span
                    animate={{ x: emotionOptIn ? 24 : 0 }}
                    className="inline-block h-4 w-4 transform rounded-full bg-white transition-transform"
                  />
                </motion.button>
              </div>

              {emotionOptIn && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  className="p-4 bg-blue-50 rounded-lg"
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="font-medium text-blue-900">Emotion Detection Status</h4>
                      <p className="text-sm text-blue-700">
                        {isCapturing ? 'Currently active' : 'Ready to start'}
                      </p>
                    </div>
                    <motion.button
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                      onClick={() => isCapturing ? stopCapture() : startCapture()}
                      className={`px-4 py-2 rounded-lg text-sm font-medium ${
                        isCapturing
                          ? 'bg-red-100 text-red-700 hover:bg-red-200'
                          : 'bg-blue-100 text-blue-700 hover:bg-blue-200'
                      }`}
                    >
                      {isCapturing ? 'Stop Detection' : 'Start Detection'}
                    </motion.button>
                  </div>
                </motion.div>
              )}

              <div className="p-4 bg-yellow-50 rounded-lg">
                <h4 className="font-medium text-yellow-900 mb-2">Privacy Notice</h4>
                <p className="text-sm text-yellow-800">
                  Your emotion data is processed locally and only stored with your consent. 
                  We never share your personal data with third parties. You can disable 
                  emotion detection at any time.
                </p>
              </div>
            </div>
          </div>

          {/* Learning Preferences */}
          <div className="card">
            <div className="flex items-center space-x-3 mb-6">
              <Palette className="w-6 h-6 text-purple-600" />
              <h2 className="text-xl font-semibold text-gray-900">Learning Preferences</h2>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Difficulty Level
                </label>
                <select className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent">
                  <option value="beginner">Beginner</option>
                  <option value="intermediate">Intermediate</option>
                  <option value="advanced">Advanced</option>
                  <option value="adaptive">Adaptive (Recommended)</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Learning Style
                </label>
                <select className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent">
                  <option value="visual">Visual</option>
                  <option value="auditory">Auditory</option>
                  <option value="kinesthetic">Kinesthetic</option>
                  <option value="mixed">Mixed</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Study Session Length
                </label>
                <select className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent">
                  <option value="15">15 minutes</option>
                  <option value="30">30 minutes</option>
                  <option value="45">45 minutes</option>
                  <option value="60">60 minutes</option>
                </select>
              </div>
            </div>
          </div>

          {/* Co-Learner Settings */}
          <CoLearnerSettings />

          {/* Notifications */}
          <div className="card">
            <div className="flex items-center space-x-3 mb-6">
              <Bell className="w-6 h-6 text-green-600" />
              <h2 className="text-xl font-semibold text-gray-900">Notifications</h2>
            </div>

            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-medium text-gray-900">Study Reminders</h3>
                  <p className="text-sm text-gray-600">Get notified to start your daily study session</p>
                </div>
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className="relative inline-flex h-6 w-11 items-center rounded-full bg-blue-600"
                >
                  <span className="inline-block h-4 w-4 transform rounded-full bg-white translate-x-6" />
                </motion.button>
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-medium text-gray-900">Achievement Notifications</h3>
                  <p className="text-sm text-gray-600">Celebrate when you earn new badges</p>
                </div>
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className="relative inline-flex h-6 w-11 items-center rounded-full bg-blue-600"
                >
                  <span className="inline-block h-4 w-4 transform rounded-full bg-white translate-x-6" />
                </motion.button>
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-medium text-gray-900">Emotion Insights</h3>
                  <p className="text-sm text-gray-600">Weekly reports on your learning emotions</p>
                </div>
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className="relative inline-flex h-6 w-11 items-center rounded-full bg-gray-200"
                >
                  <span className="inline-block h-4 w-4 transform rounded-full bg-white" />
                </motion.button>
              </div>
            </div>
          </div>

          {/* Save Button */}
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            className="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white py-3 px-6 rounded-lg font-medium hover:from-blue-700 hover:to-purple-700 transition-all duration-200"
          >
            Save Settings
          </motion.button>
        </motion.div>
      </div>
    </div>
  )
}
