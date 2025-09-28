import { useState, useCallback } from 'react';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'https://neurolearn-6c0k.onrender.com';

export const useStory = (token) => {
  const [storyData, setStoryData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [rewards, setRewards] = useState([]);
  const [showRewards, setShowRewards] = useState(false);

  const fetchStoryData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch(`${API_BASE_URL}/api/story/current`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error('Failed to fetch story data');
      }

      const result = await response.json();
      setStoryData(result.data);
      return result.data;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [token]);

  const updateStoryProgress = useCallback(async (questId, score, timeSpent = 0) => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch(`${API_BASE_URL}/api/story/progress`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          quest_id: questId,
          score: score,
          time_spent: timeSpent
        })
      });

      if (!response.ok) {
        throw new Error('Failed to update story progress');
      }

      const result = await response.json();
      
      // Show rewards if any
      if (result.data.rewards && result.data.rewards.length > 0) {
        setRewards(result.data.rewards);
        setShowRewards(true);
      }

      // Refresh story data
      await fetchStoryData();
      
      return result.data;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [token, fetchStoryData]);

  const getStoryRewards = useCallback(async (storyId) => {
    try {
      const response = await fetch(`/api/story/rewards?story_id=${storyId}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error('Failed to fetch story rewards');
      }

      const result = await response.json();
      return result.rewards;
    } catch (err) {
      setError(err.message);
      throw err;
    }
  }, [token]);

  const markRewardViewed = useCallback(async (rewardId) => {
    try {
      const response = await fetch(`/api/story/rewards/${rewardId}/viewed`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error('Failed to mark reward as viewed');
      }

      return true;
    } catch (err) {
      setError(err.message);
      return false;
    }
  }, [token]);

  const getChapterDetails = useCallback(async (chapterId) => {
    try {
      const response = await fetch(`/api/story/chapters/${chapterId}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error('Failed to fetch chapter details');
      }

      const result = await response.json();
      return result.chapter;
    } catch (err) {
      setError(err.message);
      throw err;
    }
  }, [token]);

  const getQuestDetails = useCallback(async (questId) => {
    try {
      const response = await fetch(`/api/story/quests/${questId}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error('Failed to fetch quest details');
      }

      const result = await response.json();
      return result.quest;
    } catch (err) {
      setError(err.message);
      throw err;
    }
  }, [token]);

  const startStory = useCallback(async (storyId) => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch(`/api/story/stories/${storyId}/start`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error('Failed to start story');
      }

      const result = await response.json();
      
      // Refresh story data
      await fetchStoryData();
      
      return result;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [token, fetchStoryData]);

  const closeRewards = useCallback(() => {
    setShowRewards(false);
    setRewards([]);
  }, []);

  return {
    storyData,
    loading,
    error,
    rewards,
    showRewards,
    fetchStoryData,
    updateStoryProgress,
    getStoryRewards,
    markRewardViewed,
    getChapterDetails,
    getQuestDetails,
    startStory,
    closeRewards
  };
};
