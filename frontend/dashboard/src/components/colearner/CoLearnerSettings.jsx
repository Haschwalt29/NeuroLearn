import React, { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import axios from 'axios'
import { useAuth } from '../../contexts/AuthContext'
import { Check, X, Settings } from 'lucide-react'

const PERSONA_OPTIONS = [
  { value: 'curious_companion', label: 'Curious Companion (Nova)', description: 'Playful and asks questions' },
  { value: 'zen_coach', label: 'Zen Coach (Asha)', description: 'Calm and supportive' },
  { value: 'challenger', label: 'Challenger (Rex)', description: 'Pushes your limits' }
]

export default function CoLearnerSettings() {
  const { token } = useAuth()
  const [loading, setLoading] = useState(false)
  const [saving, setSaving] = useState(false)
  const [settings, setSettings] = useState({
    enabled: false,
    save_dialogs: false,
    persona: 'curious_companion',
    humor_level: 3
  })
  const [profile, setProfile] = useState(null)

  useEffect(() => {
    fetchSettings()
  }, [token])

  const fetchSettings = async () => {
    try {
      setLoading(true)
      const response = await axios.get('/api/colearner/state', {
        headers: { Authorization: `Bearer ${token}` }
      })
      const profileData = response.data.profile
      setProfile(profileData)
      setSettings({
        enabled: profileData.settings?.enabled || false,
        save_dialogs: profileData.settings?.save_dialogs || false,
        persona: profileData.persona_config?.name?.toLowerCase().replace(' ', '_') || 'curious_companion',
        humor_level: profileData.humor_level || 3
      })
    } catch (error) {
      console.error('Failed to fetch co-learner settings:', error)
    } finally {
      setLoading(false)
    }
  }

  const saveSettings = async () => {
    try {
      setSaving(true)
      const personaPreset = PERSONA_OPTIONS.find(p => p.value === settings.persona)
      const personaConfig = {
        name: personaPreset?.label.split(' ')[0] || 'Nova',
        tone: settings.persona === 'zen_coach' ? 'calm' : settings.persona === 'challenger' ? 'challenging' : 'playful'
      }

      await axios.post('/api/colearner/settings', {
        enabled: settings.enabled,
        save_dialogs: settings.save_dialogs,
        persona: personaConfig,
        humor_level: settings.humor_level
      }, {
        headers: { Authorization: `Bearer ${token}` }
      })

      // Refresh settings
      await fetchSettings()
    } catch (error) {
      console.error('Failed to save co-learner settings:', error)
    } finally {
      setSaving(false)
    }
  }

  const handleToggle = (key) => {
    setSettings(prev => ({ ...prev, [key]: !prev[key] }))
  }

  const handlePersonaChange = (value) => {
    setSettings(prev => ({ ...prev, persona: value }))
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white rounded-lg shadow-md p-6"
    >
      <div className="flex items-center gap-3 mb-6">
        <Settings className="w-6 h-6 text-blue-600" />
        <h3 className="text-xl font-semibold text-gray-800">AI Co-Learner Settings</h3>
      </div>

      <div className="space-y-6">
        {/* Enable/Disable Toggle */}
        <div className="flex items-center justify-between">
          <div>
            <h4 className="text-lg font-medium text-gray-700">Enable Co-Learner</h4>
            <p className="text-sm text-gray-500">Let an AI study buddy join your learning journey</p>
          </div>
          <button
            onClick={() => handleToggle('enabled')}
            className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
              settings.enabled ? 'bg-blue-600' : 'bg-gray-200'
            }`}
          >
            <span
              className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                settings.enabled ? 'translate-x-6' : 'translate-x-1'
              }`}
            />
          </button>
        </div>

        {/* Save Dialogs Toggle */}
        <div className="flex items-center justify-between">
          <div>
            <h4 className="text-lg font-medium text-gray-700">Save Conversations</h4>
            <p className="text-sm text-gray-500">Store chat history for better personalization</p>
          </div>
          <button
            onClick={() => handleToggle('save_dialogs')}
            className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
              settings.save_dialogs ? 'bg-blue-600' : 'bg-gray-200'
            }`}
          >
            <span
              className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                settings.save_dialogs ? 'translate-x-6' : 'translate-x-1'
              }`}
            />
          </button>
        </div>

        {/* Persona Selection */}
        <div>
          <h4 className="text-lg font-medium text-gray-700 mb-3">Choose Your Co-Learner</h4>
          <div className="space-y-3">
            {PERSONA_OPTIONS.map((option) => (
              <label key={option.value} className="flex items-start gap-3 cursor-pointer">
                <input
                  type="radio"
                  name="persona"
                  value={option.value}
                  checked={settings.persona === option.value}
                  onChange={(e) => handlePersonaChange(e.target.value)}
                  className="mt-1 h-4 w-4 text-blue-600 focus:ring-blue-500"
                />
                <div className="flex-1">
                  <div className="font-medium text-gray-700">{option.label}</div>
                  <div className="text-sm text-gray-500">{option.description}</div>
                </div>
              </label>
            ))}
          </div>
        </div>

        {/* Humor Level */}
        <div>
          <h4 className="text-lg font-medium text-gray-700 mb-3">Humor Level</h4>
          <div className="flex items-center gap-4">
            <span className="text-sm text-gray-600">Serious</span>
            <input
              type="range"
              min="0"
              max="10"
              value={settings.humor_level}
              onChange={(e) => setSettings(prev => ({ ...prev, humor_level: parseInt(e.target.value) }))}
              className="flex-1"
            />
            <span className="text-sm text-gray-600">Hilarious</span>
          </div>
          <div className="text-center text-sm text-gray-500 mt-1">
            Level {settings.humor_level}/10
          </div>
        </div>

        {/* Current Status */}
        {profile && (
          <div className="bg-gray-50 rounded-lg p-4">
            <h5 className="font-medium text-gray-700 mb-2">Current Status</h5>
            <div className="text-sm text-gray-600 space-y-1">
              <div>Level: {profile.level || 1} | XP: {profile.xp || 0}</div>
              <div>Traits: {profile.traits?.join(', ') || 'None'}</div>
              <div>Persona: {profile.persona_config?.name || 'Not set'}</div>
              <div>Status: {settings.enabled ? 'Active' : 'Inactive'}</div>
            </div>
          </div>
        )}

        {/* Save Button */}
        <div className="flex justify-end">
          <motion.button
            onClick={saveSettings}
            disabled={saving}
            className="flex items-center gap-2 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            {saving ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                Saving...
              </>
            ) : (
              <>
                <Check className="w-4 h-4" />
                Save Settings
              </>
            )}
          </motion.button>
        </div>
      </div>
    </motion.div>
  )
}
