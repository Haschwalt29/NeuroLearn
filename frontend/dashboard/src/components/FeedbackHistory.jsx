import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'https://neurolearn-6c0k.onrender.com';

const FeedbackHistory = ({ userId, token }) => {
  const [feedbackHistory, setFeedbackHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchFeedbackHistory();
  }, [userId, token]);

  const fetchFeedbackHistory = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE_URL}/api/feedback/history`, {
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
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (timestamp) => {
    return new Date(timestamp).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getFeedbackTypeIcon = (type) => {
    const icons = {
      lesson: '📚',
      quiz: '📝',
      milestone: '🏆',
      default: '💬'
    };
    return icons[type] || icons.default;
  };

  const getPerformanceColor = (accuracy) => {
    if (accuracy >= 80) return 'text-green-600';
    if (accuracy >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <span className="ml-2 text-gray-600">Loading feedback history...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <div className="flex items-center">
          <svg className="w-5 h-5 text-red-400 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span className="text-gray-600">No feedback history available.</span>
        </div>
      </div>
    );
  }

  if (feedbackHistory.length === 0) {
    return (
      <div className="text-center p-8 text-gray-500">
        <div className="text-4xl mb-4">💭</div>
        <h3 className="text-lg font-semibold mb-2">No feedback yet</h3>
        <p className="text-sm">Complete some lessons to see your personalized feedback!</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold text-gray-800">Feedback History</h2>
        <button
          onClick={fetchFeedbackHistory}
          className="text-blue-600 hover:text-blue-800 text-sm font-medium"
        >
          Refresh
        </button>
      </div>

      <div className="space-y-3">
        {feedbackHistory.map((feedback, index) => (
          <motion.div
            key={feedback.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className="bg-white rounded-lg border border-gray-200 p-4 hover:shadow-md transition-shadow"
          >
            <div className="flex items-start justify-between mb-3">
              <div className="flex items-center space-x-2">
                <span className="text-lg">{getFeedbackTypeIcon(feedback.feedback_type)}</span>
                <div>
                  <h3 className="font-semibold text-gray-800 capitalize">
                    {feedback.feedback_type} Feedback
                  </h3>
                  <p className="text-sm text-gray-500">
                    {formatDate(feedback.timestamp)}
                  </p>
                </div>
              </div>
              {feedback.performance_data?.accuracy && (
                <div className={`text-sm font-semibold ${getPerformanceColor(feedback.performance_data.accuracy)}`}>
                  {feedback.performance_data.accuracy.toFixed(1)}%
                </div>
              )}
            </div>

            <div className="mb-3">
              <p className="text-gray-700 leading-relaxed">
                {feedback.feedback_text}
              </p>
            </div>

            {/* Performance details */}
            {feedback.performance_data && (
              <div className="bg-gray-50 rounded-lg p-3 mb-3">
                <h4 className="text-sm font-semibold text-gray-700 mb-2">Performance Details</h4>
                <div className="grid grid-cols-2 gap-2 text-xs">
                  <div>
                    <span className="text-gray-600">Questions:</span>
                    <span className="ml-1 font-semibold">
                      {feedback.performance_data.total_questions || 0}
                    </span>
                  </div>
                  <div>
                    <span className="text-gray-600">Correct:</span>
                    <span className="ml-1 font-semibold">
                      {feedback.performance_data.correct_answers || 0}
                    </span>
                  </div>
                  {feedback.performance_data.strong_topics?.length > 0 && (
                    <div className="col-span-2">
                      <span className="text-gray-600">Strong in:</span>
                      <span className="ml-1 font-semibold text-green-600">
                        {feedback.performance_data.strong_topics.join(', ')}
                      </span>
                    </div>
                  )}
                  {feedback.performance_data.weak_topics?.length > 0 && (
                    <div className="col-span-2">
                      <span className="text-gray-600">Needs work:</span>
                      <span className="ml-1 font-semibold text-red-600">
                        {feedback.performance_data.weak_topics.join(', ')}
                      </span>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Emotion context */}
            {feedback.emotion_context?.dominant_emotion && (
              <div className="flex items-center space-x-2 text-sm">
                <span className="text-gray-600">Mood:</span>
                <span className="capitalize font-medium text-gray-700">
                  {feedback.emotion_context.dominant_emotion.replace('_', ' ')}
                </span>
              </div>
            )}
          </motion.div>
        ))}
      </div>
    </div>
  );
};

export default FeedbackHistory;
