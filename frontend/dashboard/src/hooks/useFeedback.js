import { useState, useEffect, useCallback } from 'react';
import { useCoLearner } from './useCoLearner';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'https://neurolearn-6c0k.onrender.com';

export const useFeedback = (token) => {
  const [currentFeedback, setCurrentFeedback] = useState(null);
  const [feedbackHistory, setFeedbackHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const { notifyLessonComplete, notifyQuizComplete } = useCoLearner(token);

  const generateFeedback = useCallback(async (lessonId = null) => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch(`${API_BASE_URL}/api/feedback/generate`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ lesson_id: lessonId })
      });

      if (!response.ok) {
        throw new Error('Failed to generate feedback');
      }

      const data = await response.json();
      setCurrentFeedback(data);
      return data;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [token]);

  const completeLesson = useCallback(async (lessonData) => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch(`${API_BASE_URL}/api/feedback/lesson/complete`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(lessonData)
      });

      if (!response.ok) {
        throw new Error('Failed to complete lesson');
      }

      const data = await response.json();
      setCurrentFeedback(data.feedback);
      
      // Notify co-learner about lesson completion
      try {
        await notifyLessonComplete(lessonData);
      } catch (coLearnerError) {
        console.warn('Co-learner notification failed:', coLearnerError);
      }
      
      return data;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [token, notifyLessonComplete]);

  const completeQuiz = useCallback(async (quizData) => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch(`${API_BASE_URL}/api/feedback/quiz/complete`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(quizData)
      });

      if (!response.ok) {
        throw new Error('Failed to complete quiz');
      }

      const data = await response.json();
      setCurrentFeedback(data.feedback);
      
      // Notify co-learner about quiz completion
      try {
        await notifyQuizComplete(quizData);
      } catch (coLearnerError) {
        console.warn('Co-learner notification failed:', coLearnerError);
      }
      
      return data;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [token, notifyQuizComplete]);

  const fetchFeedbackHistory = useCallback(async (limit = 10) => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch(`/api/feedback/history?limit=${limit}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error('Failed to fetch feedback history');
      }

      const data = await response.json();
      setFeedbackHistory(data.feedback_history || []);
      return data.feedback_history;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [token]);

  const getLatestFeedback = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch(`${API_BASE_URL}/api/feedback/latest`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        if (response.status === 404) {
          return null; // No feedback available
        }
        throw new Error('Failed to get latest feedback');
      }

      const data = await response.json();
      setCurrentFeedback(data);
      return data;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [token]);

  const getFeedbackStats = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch(`${API_BASE_URL}/api/feedback/stats`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error('Failed to get feedback stats');
      }

      const data = await response.json();
      return data;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [token]);

  const checkMilestone = useCallback(async (milestoneType) => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch(`/api/feedback/milestone/${milestoneType}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error('Failed to check milestone');
      }

      const data = await response.json();
      
      if (data.milestone_achieved) {
        setCurrentFeedback({
          feedback_text: data.message,
          feedback_type: 'milestone',
          performance_data: { milestone_type: milestoneType }
        });
      }
      
      return data;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [token]);

  const clearCurrentFeedback = useCallback(() => {
    setCurrentFeedback(null);
  }, []);

  return {
    currentFeedback,
    feedbackHistory,
    loading,
    error,
    generateFeedback,
    completeLesson,
    completeQuiz,
    fetchFeedbackHistory,
    getLatestFeedback,
    getFeedbackStats,
    checkMilestone,
    clearCurrentFeedback
  };
};
