import { useState, useEffect, useCallback } from 'react';
import { useCoLearner } from './useCoLearner';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'https://neurolearn-6c0k.onrender.com';

export const useRevision = (userId, token) => {
  const [dueReviews, setDueReviews] = useState([]);
  const [calendarData, setCalendarData] = useState({});
  const [stats, setStats] = useState(null);
  const { notifyReviewComplete } = useCoLearner(token);
  const [insights, setInsights] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchDueReviews = useCallback(async (limit = 20, overdueOnly = false) => {
    if (!userId || !token) return;

    try {
      setLoading(true);
      setError(null);

      const params = new URLSearchParams({
        limit: limit.toString(),
        overdue_only: overdueOnly.toString()
      });

      const response = await fetch(`${API_BASE_URL}/api/revision/due?${params}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error('Failed to fetch due reviews');
      }

      const data = await response.json();
      setDueReviews(data.due_reviews || []);
      return data;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [userId, token]);

  const fetchCalendarData = useCallback(async (startDate, endDate) => {
    if (!userId || !token) return;

    try {
      setLoading(true);
      setError(null);

      const params = new URLSearchParams({
        start: startDate.toISOString(),
        end: endDate.toISOString()
      });

      const response = await fetch(`${API_BASE_URL}/api/revision/calendar?${params}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error('Failed to fetch calendar data');
      }

      const data = await response.json();
      setCalendarData(data.calendar || {});
      return data;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [userId, token]);

  const fetchStats = useCallback(async () => {
    if (!userId || !token) return;

    try {
      setLoading(true);
      setError(null);

      const response = await fetch(`${API_BASE_URL}/api/revision/stats`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error('Failed to fetch revision stats');
      }

      const data = await response.json();
      setStats(data);
      return data;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [userId, token]);

  const fetchInsights = useCallback(async () => {
    if (!userId || !token) return;

    try {
      setLoading(true);
      setError(null);

      const response = await fetch(`${API_BASE_URL}/api/revision/insights`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error('Failed to fetch revision insights');
      }

      const data = await response.json();
      setInsights(data);
      return data;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [userId, token]);

  const completeReview = useCallback(async (contentId, qualityScore, emotionHint = null, responseTime = null) => {
    if (!userId || !token) return;

    try {
      setLoading(true);
      setError(null);

      const response = await fetch(`${API_BASE_URL}/api/revision/complete`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          content_id: contentId,
          quality_score: qualityScore,
          emotion_hint: emotionHint,
          response_time: responseTime
        })
      });

      if (!response.ok) {
        throw new Error('Failed to complete review');
      }

      const data = await response.json();
      
      // Notify co-learner about review completion
      try {
        await notifyReviewComplete({
          content_id: contentId,
          quality_score: qualityScore,
          response_time: responseTime,
          topic: data.topic
        });
      } catch (coLearnerError) {
        console.warn('Co-learner notification failed:', coLearnerError);
      }
      
      // Refresh data after completion
      await fetchDueReviews();
      await fetchStats();
      
      return data;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [userId, token, fetchDueReviews, fetchStats, notifyReviewComplete]);

  const snoozeReview = useCallback(async (contentId, days = 1) => {
    if (!userId || !token) return;

    try {
      setLoading(true);
      setError(null);

      const response = await fetch(`${API_BASE_URL}/api/revision/snooze`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          content_id: contentId,
          days: days
        })
      });

      if (!response.ok) {
        throw new Error('Failed to snooze review');
      }

      const data = await response.json();
      
      // Refresh data after snoozing
      await fetchDueReviews();
      
      return data;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [userId, token, fetchDueReviews]);

  const scheduleInitialReview = useCallback(async (contentId, topic = null) => {
    if (!userId || !token) return;

    try {
      setLoading(true);
      setError(null);

      const response = await fetch(`${API_BASE_URL}/api/revision/schedule`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          content_id: contentId,
          topic: topic
        })
      });

      if (!response.ok) {
        throw new Error('Failed to schedule review');
      }

      const data = await response.json();
      
      // Refresh data after scheduling
      await fetchDueReviews();
      await fetchStats();
      
      return data;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [userId, token, fetchDueReviews, fetchStats]);

  const getContentSchedule = useCallback(async (contentId) => {
    if (!userId || !token) return;

    try {
      setLoading(true);
      setError(null);

      const response = await fetch(`${API_BASE_URL}/api/revision/schedule/${contentId}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error('Failed to get content schedule');
      }

      const data = await response.json();
      return data;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [userId, token]);

  const deleteContentSchedule = useCallback(async (contentId) => {
    if (!userId || !token) return;

    try {
      setLoading(true);
      setError(null);

      const response = await fetch(`${API_BASE_URL}/api/revision/schedule/${contentId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error('Failed to delete content schedule');
      }

      const data = await response.json();
      
      // Refresh data after deletion
      await fetchDueReviews();
      await fetchStats();
      
      return data;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [userId, token, fetchDueReviews, fetchStats]);

  // Auto-fetch initial data
  useEffect(() => {
    if (userId && token) {
      fetchDueReviews();
      fetchStats();
    }
  }, [userId, token, fetchDueReviews, fetchStats]);

  return {
    // Data
    dueReviews,
    calendarData,
    stats,
    insights,
    loading,
    error,
    
    // Actions
    fetchDueReviews,
    fetchCalendarData,
    fetchStats,
    fetchInsights,
    completeReview,
    snoozeReview,
    scheduleInitialReview,
    getContentSchedule,
    deleteContentSchedule,
    
    // Computed values
    overdueCount: dueReviews.filter(r => r.overdue_days > 0).length,
    dueTodayCount: dueReviews.filter(r => r.overdue_days === 0).length,
    totalDueCount: dueReviews.length
  };
};
