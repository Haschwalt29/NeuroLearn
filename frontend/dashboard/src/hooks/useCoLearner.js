import { useState, useCallback } from 'react'
import { useSocket } from '../contexts/SocketContext'

export const useCoLearner = (token) => {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const { on, emit } = useSocket()

  const notifyLessonComplete = useCallback(async (lessonData) => {
    if (!token) return

    try {
      setLoading(true)
      setError(null)

      const response = await fetch('/api/colearner/action', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          activity_type: 'lesson_complete',
          payload: {
            lesson_id: lessonData.lesson_id || lessonData.id,
            module: lessonData.module || 'general',
            score: lessonData.score || 0,
            time_taken_s: lessonData.time_taken_s || 0,
            topic: lessonData.topic,
            mastery: lessonData.mastery
          }
        })
      })

      if (!response.ok) {
        throw new Error('Failed to notify co-learner')
      }

      const result = await response.json()
      return result
    } catch (err) {
      setError(err.message)
      console.error('Co-learner notification failed:', err)
      throw err
    } finally {
      setLoading(false)
    }
  }, [token])

  const notifyQuizComplete = useCallback(async (quizData) => {
    if (!token) return

    try {
      setLoading(true)
      setError(null)

      const response = await fetch('/api/colearner/action', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          activity_type: 'quiz_complete',
          payload: {
            quiz_id: quizData.quiz_id || quizData.id,
            module: quizData.module || 'general',
            score: quizData.score || 0,
            correct_answers: quizData.correct_answers || 0,
            total_questions: quizData.total_questions || 0,
            time_taken_s: quizData.time_taken_s || 0,
            topic: quizData.topic
          }
        })
      })

      if (!response.ok) {
        throw new Error('Failed to notify co-learner')
      }

      const result = await response.json()
      return result
    } catch (err) {
      setError(err.message)
      console.error('Co-learner notification failed:', err)
      throw err
    } finally {
      setLoading(false)
    }
  }, [token])

  const notifyReviewComplete = useCallback(async (reviewData) => {
    if (!token) return

    try {
      setLoading(true)
      setError(null)

      const response = await fetch('/api/colearner/action', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          activity_type: 'review_complete',
          payload: {
            content_id: reviewData.content_id,
            quality_score: reviewData.quality_score,
            response_time: reviewData.response_time,
            topic: reviewData.topic
          }
        })
      })

      if (!response.ok) {
        throw new Error('Failed to notify co-learner')
      }

      const result = await response.json()
      return result
    } catch (err) {
      setError(err.message)
      console.error('Co-learner notification failed:', err)
      throw err
    } finally {
      setLoading(false)
    }
  }, [token])

  const mirrorEmotion = useCallback(async (emotion, confidence) => {
    if (!token) return

    try {
      const response = await fetch('/api/colearner/mirror_emotion', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          emotion,
          confidence: confidence || 0.5
        })
      })

      if (!response.ok) {
        throw new Error('Failed to mirror emotion')
      }

      const result = await response.json()
      return result
    } catch (err) {
      setError(err.message)
      console.error('Emotion mirroring failed:', err)
      throw err
    }
  }, [token])

  return {
    loading,
    error,
    notifyLessonComplete,
    notifyQuizComplete,
    notifyReviewComplete,
    mirrorEmotion
  }
}
