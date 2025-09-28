import React, { createContext, useContext, useState, useEffect, useRef } from 'react'
import { useAuth } from './AuthContext'
import { useSocket } from './SocketContext'
import toast from 'react-hot-toast'

const EmotionContext = createContext()

export function useEmotion() {
  const context = useContext(EmotionContext)
  if (!context) {
    throw new Error('useEmotion must be used within an EmotionProvider')
  }
  return context
}

export function EmotionProvider({ children }) {
  const [emotions, setEmotions] = useState([])
  const [currentEmotion, setCurrentEmotion] = useState(null)
  const [isCapturing, setIsCapturing] = useState(false)
  const [emotionOptIn, setEmotionOptIn] = useState(false)
  const { user } = useAuth()
  const { on, off } = useSocket()
  const videoRef = useRef(null)
  const canvasRef = useRef(null)
  const streamRef = useRef(null)
  const intervalRef = useRef(null)

  useEffect(() => {
    if (user) {
      setEmotionOptIn(user.emotion_opt_in)
    }
  }, [user])

  useEffect(() => {
    const handleEmotionUpdate = (data) => {
      if (data.user_id === user?.id) {
        const newEmotion = {
          emotion: data.emotion,
          confidence: data.confidence,
          timestamp: new Date(data.timestamp)
        }
        setCurrentEmotion(newEmotion)
        setEmotions(prev => [newEmotion, ...prev.slice(0, 99)]) // Keep last 100
      }
    }

    on('emotion_update', handleEmotionUpdate)
    return () => off('emotion_update', handleEmotionUpdate)
  }, [user, on, off])

  const startCapture = async () => {
    if (!emotionOptIn) {
      toast.error('Please enable emotion detection in settings first')
      return false
    }

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        video: { width: 640, height: 480 } 
      })
      
      if (videoRef.current) {
        videoRef.current.srcObject = stream
        streamRef.current = stream
      }

      // Start periodic capture
      intervalRef.current = setInterval(captureFrame, 5000) // Every 5 seconds
      setIsCapturing(true)
      
      toast.success('Emotion detection started')
      return true
    } catch (error) {
      console.error('Error accessing camera:', error)
      toast.error('Could not access camera. Please check permissions.')
      return false
    }
  }

  const stopCapture = () => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current)
      intervalRef.current = null
    }

    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop())
      streamRef.current = null
    }

    setIsCapturing(false)
    setCurrentEmotion(null)
    toast.success('Emotion detection stopped')
  }

  const captureFrame = async () => {
    if (!videoRef.current || !canvasRef.current) return

    const video = videoRef.current
    const canvas = canvasRef.current
    const ctx = canvas.getContext('2d')

    canvas.width = video.videoWidth
    canvas.height = video.videoHeight
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height)

    const dataUrl = canvas.toDataURL('image/jpeg', 0.8)
    
    try {
      const response = await fetch('/api/emotion', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({ image: dataUrl })
      })

      if (response.ok) {
        const data = await response.json()
        // Emotion will be handled by WebSocket update
      }
    } catch (error) {
      console.error('Error sending emotion data:', error)
    }
  }

  const toggleEmotionOptIn = async (enabled) => {
    try {
      const response = await fetch('/api/settings/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({ emotion_opt_in: enabled })
      })

      if (response.ok) {
        setEmotionOptIn(enabled)
        if (!enabled && isCapturing) {
          stopCapture()
        }
        toast.success(enabled ? 'Emotion detection enabled' : 'Emotion detection disabled')
      }
    } catch (error) {
      console.error('Error updating emotion settings:', error)
      toast.error('Failed to update settings')
    }
  }

  const getEmotionColor = (emotion) => {
    const colors = {
      happy: '#10b981',
      sad: '#3b82f6',
      angry: '#ef4444',
      fear: '#8b5cf6',
      surprise: '#f59e0b',
      disgust: '#84cc16',
      neutral: '#6b7280'
    }
    return colors[emotion] || '#6b7280'
  }

  const getEmotionIcon = (emotion) => {
    const icons = {
      happy: '😊',
      sad: '😢',
      angry: '😠',
      fear: '😨',
      surprise: '😲',
      disgust: '🤢',
      neutral: '😐'
    }
    return icons[emotion] || '😐'
  }

  useEffect(() => {
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current)
      }
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop())
      }
    }
  }, [])

  const value = {
    emotions,
    currentEmotion,
    isCapturing,
    emotionOptIn,
    startCapture,
    stopCapture,
    toggleEmotionOptIn,
    getEmotionColor,
    getEmotionIcon,
    videoRef,
    canvasRef
  }

  return (
    <EmotionContext.Provider value={value}>
      {children}
    </EmotionContext.Provider>
  )
}
