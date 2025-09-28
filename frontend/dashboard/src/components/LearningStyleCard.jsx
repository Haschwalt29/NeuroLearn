import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Eye, Headphones, BookOpen, TrendingUp, RefreshCw, Settings } from 'lucide-react';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'https://neurolearn-6c0k.onrender.com';

const LearningStyleCard = ({ userId, token }) => {
  const [learningStyle, setLearningStyle] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [insights, setInsights] = useState(null);
  const [recommendations, setRecommendations] = useState(null);

  useEffect(() => {
    fetchLearningStyle();
  }, [userId, token]);

  const fetchLearningStyle = async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch(`${API_BASE_URL}/api/learning-style/`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error('Failed to fetch learning style');
      }

      const data = await response.json();
      setLearningStyle(data.learning_style);

      // Fetch insights and recommendations if style tracking is enabled
      if (data.learning_style_opt_in) {
        fetchInsights();
        fetchRecommendations();
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const fetchInsights = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/learning-style/insights`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        setInsights(data.insights);
      }
    } catch (err) {
      console.error('Failed to fetch insights:', err);
    }
  };

  const fetchRecommendations = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/learning-style/recommendations`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        setRecommendations(data);
      }
    } catch (err) {
      console.error('Failed to fetch recommendations:', err);
    }
  };

  const getStyleIcon = (style) => {
    switch (style) {
      case 'visual': return '📊';
      case 'auditory': return '🎧';
      case 'example': return '📚';
      default: return '🎯';
    }
  };

  const getStyleColor = (style) => {
    switch (style) {
      case 'visual': return 'from-blue-400 to-blue-600';
      case 'auditory': return 'from-green-400 to-green-600';
      case 'example': return 'from-purple-400 to-purple-600';
      default: return 'from-gray-400 to-gray-600';
    }
  };

  const getStyleName = (style) => {
    switch (style) {
      case 'visual': return 'Visual Learner';
      case 'auditory': return 'Auditory Learner';
      case 'example': return 'Example-Based Learner';
      default: return 'Balanced Learner';
    }
  };

  const getStyleDescription = (style) => {
    switch (style) {
      case 'visual': return 'You learn best through diagrams, charts, and visual content';
      case 'auditory': return 'You learn best through listening, discussions, and audio content';
      case 'example': return 'You learn best through hands-on practice and examples';
      default: return 'You adapt well to different learning styles';
    }
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-6">
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <span className="ml-2 text-gray-600">Loading learning style...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-6">
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center">
            <svg className="w-5 h-5 text-red-400 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span className="text-red-700">Error: {error}</span>
          </div>
        </div>
      </div>
    );
  }

  if (!learningStyle) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-6">
        <div className="text-center text-gray-500">
          <Settings className="w-12 h-12 mx-auto mb-4 text-gray-400" />
          <h3 className="text-lg font-semibold mb-2">Learning Style Tracking Disabled</h3>
          <p className="text-sm">Enable learning style tracking in settings to see your preferences</p>
        </div>
      </div>
    );
  }

  const { dominant_style, confidence, visual_score, auditory_score, example_score, total_attempts } = learningStyle;

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 bg-gradient-to-r from-indigo-600 to-purple-600 rounded-lg flex items-center justify-center">
            <TrendingUp className="w-6 h-6 text-white" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-gray-900">Learning Style</h2>
            <p className="text-sm text-gray-600">Your preferred learning approach</p>
          </div>
        </div>
        <button
          onClick={fetchLearningStyle}
          className="text-blue-600 hover:text-blue-800 text-sm font-medium flex items-center space-x-1"
        >
          <RefreshCw className="w-4 h-4" />
          <span>Refresh</span>
        </button>
      </div>

      {/* Dominant Style Display */}
      {dominant_style && confidence > 0.3 ? (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className={`bg-gradient-to-r ${getStyleColor(dominant_style)} rounded-lg p-6 mb-6 text-white`}
        >
          <div className="flex items-center justify-between">
            <div>
              <div className="flex items-center space-x-2 mb-2">
                <span className="text-2xl">{getStyleIcon(dominant_style)}</span>
                <h3 className="text-xl font-bold">{getStyleName(dominant_style)}</h3>
                <span className="bg-white bg-opacity-20 px-2 py-1 rounded-full text-sm font-medium">
                  {Math.round(confidence * 100)}% confident
                </span>
              </div>
              <p className="text-white text-opacity-90">{getStyleDescription(dominant_style)}</p>
            </div>
          </div>
        </motion.div>
      ) : (
        <div className="bg-gray-50 rounded-lg p-6 mb-6">
          <div className="text-center">
            <div className="flex items-center justify-center space-x-2 mb-2">
              <span className="text-2xl">🎯</span>
              <h3 className="text-xl font-bold text-gray-800">Balanced Learner</h3>
            </div>
            <p className="text-gray-600">
              {total_attempts < 3 
                ? "Complete more lessons to discover your learning style"
                : "You adapt well to different learning approaches"
              }
            </p>
          </div>
        </div>
      )}

      {/* Style Scores Chart */}
      <div className="mb-6">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">Learning Style Scores</h3>
        <div className="space-y-4">
          {/* Visual Score */}
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2 w-20">
              <Eye className="w-4 h-4 text-blue-500" />
              <span className="text-sm font-medium text-gray-700">Visual</span>
            </div>
            <div className="flex-1">
              <div className="w-full bg-gray-200 rounded-full h-3">
                <motion.div
                  className="h-3 rounded-full bg-gradient-to-r from-blue-400 to-blue-600"
                  initial={{ width: 0 }}
                  animate={{ width: `${visual_score * 100}%` }}
                  transition={{ duration: 1, delay: 0.1 }}
                />
              </div>
            </div>
            <span className="text-sm font-semibold text-gray-700 w-12 text-right">
              {Math.round(visual_score * 100)}%
            </span>
          </div>

          {/* Auditory Score */}
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2 w-20">
              <Headphones className="w-4 h-4 text-green-500" />
              <span className="text-sm font-medium text-gray-700">Auditory</span>
            </div>
            <div className="flex-1">
              <div className="w-full bg-gray-200 rounded-full h-3">
                <motion.div
                  className="h-3 rounded-full bg-gradient-to-r from-green-400 to-green-600"
                  initial={{ width: 0 }}
                  animate={{ width: `${auditory_score * 100}%` }}
                  transition={{ duration: 1, delay: 0.2 }}
                />
              </div>
            </div>
            <span className="text-sm font-semibold text-gray-700 w-12 text-right">
              {Math.round(auditory_score * 100)}%
            </span>
          </div>

          {/* Example Score */}
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2 w-20">
              <BookOpen className="w-4 h-4 text-purple-500" />
              <span className="text-sm font-medium text-gray-700">Example</span>
            </div>
            <div className="flex-1">
              <div className="w-full bg-gray-200 rounded-full h-3">
                <motion.div
                  className="h-3 rounded-full bg-gradient-to-r from-purple-400 to-purple-600"
                  initial={{ width: 0 }}
                  animate={{ width: `${example_score * 100}%` }}
                  transition={{ duration: 1, delay: 0.3 }}
                />
              </div>
            </div>
            <span className="text-sm font-semibold text-gray-700 w-12 text-right">
              {Math.round(example_score * 100)}%
            </span>
          </div>
        </div>
      </div>

      {/* Insights */}
      {insights && insights.insights.length > 0 && (
        <div className="mb-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-3">Insights</h3>
          <div className="space-y-2">
            {insights.insights.map((insight, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
                className="bg-blue-50 border border-blue-200 rounded-lg p-3"
              >
                <p className="text-blue-800 text-sm">{insight}</p>
              </motion.div>
            ))}
          </div>
        </div>
      )}

      {/* Recommendations */}
      {recommendations && recommendations.recommendations.length > 0 && (
        <div className="mb-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-3">Recommendations</h3>
          <div className="space-y-2">
            {recommendations.recommendations.map((recommendation, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
                className="bg-green-50 border border-green-200 rounded-lg p-3"
              >
                <p className="text-green-800 text-sm">{recommendation}</p>
              </motion.div>
            ))}
          </div>
        </div>
      )}

      {/* Stats */}
      <div className="bg-gray-50 rounded-lg p-4">
        <div className="flex items-center justify-between text-sm text-gray-600">
          <span>Total lessons analyzed: {total_attempts}</span>
          <span>Confidence: {Math.round(confidence * 100)}%</span>
        </div>
      </div>
    </div>
  );
};

export default LearningStyleCard;
