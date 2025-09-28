import { useState, useCallback } from 'react';

export const useLearningDNA = (token) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const updateProfile = useCallback(async (profileData) => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch('/api/dna/profile/update', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(profileData)
      });

      if (!response.ok) {
        throw new Error('Failed to update Learning DNA profile');
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

  const getProfile = useCallback(async (userId) => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch(`/api/dna/profile/dna/${userId}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error('Failed to get Learning DNA profile');
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

  const getTopicMastery = useCallback(async (userId) => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch(`/api/dna/profile/mastery/${userId}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error('Failed to get topic mastery');
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

  const getProgressHistory = useCallback(async (userId, options = {}) => {
    try {
      setLoading(true);
      setError(null);

      const params = new URLSearchParams();
      if (options.days) params.append('days', options.days);
      if (options.topic) params.append('topic', options.topic);
      if (options.limit) params.append('limit', options.limit);

      const response = await fetch(`/api/dna/profile/progress/${userId}?${params}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error('Failed to get progress history');
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

  const getTopicHistory = useCallback(async (userId, topic, days = 30) => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch(`/api/dna/profile/topic-history/${userId}/${encodeURIComponent(topic)}?days=${days}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error('Failed to get topic history');
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

  const getBadges = useCallback(async (userId) => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch(`/api/dna/badges/${userId}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error('Failed to get badges');
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

  const getLearningStats = useCallback(async (userId) => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch(`/api/dna/stats/${userId}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error('Failed to get learning stats');
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

  const getLeaderboard = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch('/api/dna/leaderboard', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error('Failed to get leaderboard');
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

  return {
    loading,
    error,
    updateProfile,
    getProfile,
    getTopicMastery,
    getProgressHistory,
    getTopicHistory,
    getBadges,
    getLearningStats,
    getLeaderboard
  };
};
