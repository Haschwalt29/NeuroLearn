import { useState, useCallback } from 'react';

export const useLearningStyle = (token) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const updateLearningStyle = useCallback(async (styleData) => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch('/api/learning-style/update', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(styleData)
      });

      if (!response.ok) {
        throw new Error('Failed to update learning style');
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

  const getLearningStyle = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch('/api/learning-style/', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error('Failed to get learning style');
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

  const getInsights = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch('/api/learning-style/insights', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error('Failed to get insights');
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

  const getRecommendations = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch('/api/learning-style/recommendations', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error('Failed to get recommendations');
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

  const getStats = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch('/api/learning-style/stats', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error('Failed to get stats');
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

  const resetLearningStyle = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch('/api/learning-style/reset', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error('Failed to reset learning style');
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
    updateLearningStyle,
    getLearningStyle,
    getInsights,
    getRecommendations,
    getStats,
    resetLearningStyle
  };
};
