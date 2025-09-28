import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Clock, Play, Calendar, AlertCircle, CheckCircle } from 'lucide-react';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'https://neurolearn-6c0k.onrender.com';

const DueNowPanel = ({ userId, token }) => {
  const [dueReviews, setDueReviews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchDueReviews();
  }, [userId, token]);

  const fetchDueReviews = async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch(`${API_BASE_URL}/api/revision/due?limit=3`, {
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
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const startReview = async (review) => {
    // This would typically open a review modal or navigate to review page
    console.log('Starting review:', review);
    // For now, just show an alert
    alert(`Starting review for: ${review.topic}`);
  };

  const snoozeReview = async (contentId, days = 1) => {
    try {
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

      if (response.ok) {
        // Refresh the list
        fetchDueReviews();
      }
    } catch (err) {
      console.error('Failed to snooze review:', err);
    }
  };

  const getPriorityColor = (overdueDays) => {
    if (overdueDays > 0) return 'text-red-600 bg-red-50 border-red-200';
    if (overdueDays === 0) return 'text-orange-600 bg-orange-50 border-orange-200';
    return 'text-blue-600 bg-blue-50 border-blue-200';
  };

  const getPriorityIcon = (overdueDays) => {
    if (overdueDays > 0) return <AlertCircle className="w-4 h-4" />;
    if (overdueDays === 0) return <Clock className="w-4 h-4" />;
    return <Calendar className="w-4 h-4" />;
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-6">
        <div className="flex items-center justify-center h-32">
          <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
          <span className="ml-2 text-gray-600">Loading reviews...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-6">
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center">
            <AlertCircle className="w-5 h-5 text-red-400 mr-2" />
            <span className="text-red-700">Error: {error}</span>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-2">
          <Clock className="w-5 h-5 text-blue-600" />
          <h3 className="text-lg font-semibold text-gray-900">Due Reviews</h3>
        </div>
        <button
          onClick={fetchDueReviews}
          className="text-blue-600 hover:text-blue-800 text-sm font-medium"
        >
          Refresh
        </button>
      </div>

      {/* Reviews List */}
      {dueReviews.length === 0 ? (
        <div className="text-center py-8">
          <CheckCircle className="w-12 h-12 text-green-500 mx-auto mb-3" />
          <h4 className="text-lg font-medium text-gray-900 mb-2">All caught up!</h4>
          <p className="text-gray-600">No reviews due at the moment.</p>
        </div>
      ) : (
        <div className="space-y-3">
          <AnimatePresence>
            {dueReviews.map((review, index) => (
              <motion.div
                key={review.schedule_id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ delay: index * 0.1 }}
                className={`border rounded-lg p-4 ${getPriorityColor(review.overdue_days)}`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-2">
                      {getPriorityIcon(review.overdue_days)}
                      <h4 className="font-medium">{review.topic}</h4>
                      {review.overdue_days > 0 && (
                        <span className="text-xs bg-red-100 text-red-700 px-2 py-1 rounded-full">
                          {review.overdue_days} day{review.overdue_days > 1 ? 's' : ''} overdue
                        </span>
                      )}
                    </div>
                    
                    {review.content && (
                      <p className="text-sm text-gray-700 mb-2 line-clamp-2">
                        {review.content.question}
                      </p>
                    )}
                    
                    <div className="flex items-center space-x-4 text-xs text-gray-600">
                      <span>Interval: {review.interval_days} days</span>
                      <span>Repetitions: {review.repetitions}</span>
                      <span>EF: {review.easiness_factor.toFixed(2)}</span>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-2 ml-4">
                    <motion.button
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                      onClick={() => startReview(review)}
                      className="flex items-center space-x-1 px-3 py-1 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700"
                    >
                      <Play className="w-3 h-3" />
                      <span>Start</span>
                    </motion.button>
                    
                    <motion.button
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                      onClick={() => snoozeReview(review.content_id, 1)}
                      className="px-2 py-1 text-gray-600 hover:text-gray-800 text-sm"
                    >
                      Snooze
                    </motion.button>
                  </div>
                </div>
              </motion.div>
            ))}
          </AnimatePresence>
        </div>
      )}

      {/* Footer */}
      {dueReviews.length > 0 && (
        <div className="mt-4 pt-4 border-t border-gray-200">
          <div className="flex items-center justify-between text-sm text-gray-600">
            <span>
              {dueReviews.filter(r => r.overdue_days > 0).length} overdue, {' '}
              {dueReviews.filter(r => r.overdue_days === 0).length} due today
            </span>
            <button className="text-blue-600 hover:text-blue-800 font-medium">
              View All Reviews
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default DueNowPanel;
