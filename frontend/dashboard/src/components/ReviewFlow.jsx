import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  BookOpen, 
  Clock, 
  CheckCircle, 
  XCircle, 
  RotateCcw, 
  ArrowRight,
  Star,

  AlertCircle
} from 'lucide-react';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'https://neurolearn-6c0k.onrender.com';

const ReviewFlow = ({ userId, token, onComplete }) => {
  const [currentReview, setCurrentReview] = useState(null);
  const [qualityScore, setQualityScore] = useState(null);
  const [responseTime, setResponseTime] = useState(0);
  const [showAnswer, setShowAnswer] = useState(false);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const [startTime, setStartTime] = useState(null);

  useEffect(() => {
    fetchNextReview();
  }, [userId, token]);

  useEffect(() => {
    if (currentReview && !startTime) {
      setStartTime(Date.now());
    }
  }, [currentReview, startTime]);

  const fetchNextReview = async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch(`${API_BASE_URL}/api/revision/due?limit=1`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error('Failed to fetch review');
      }

      const data = await response.json();
      const reviews = data.due_reviews || [];
      
      if (reviews.length === 0) {
        setCurrentReview(null);
      } else {
        setCurrentReview(reviews[0]);
        setStartTime(Date.now());
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleShowAnswer = () => {
    setShowAnswer(true);
    setResponseTime(Date.now() - startTime);
  };

  const handleQualitySelect = async (score) => {
    if (!currentReview) return;

    setQualityScore(score);
    setSubmitting(true);

    try {
      const response = await fetch(`${API_BASE_URL}/api/revision/complete`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          content_id: currentReview.content_id,
          quality_score: score,
          response_time: responseTime / 1000 // Convert to seconds
        })
      });

      if (!response.ok) {
        throw new Error('Failed to submit review');
      }

      const result = await response.json();
      
      // Call completion callback if provided
      if (onComplete) {
        onComplete(result);
      }

      // Move to next review
      setTimeout(() => {
        setCurrentReview(null);
        setQualityScore(null);
        setShowAnswer(false);
        setResponseTime(0);
        setStartTime(null);
        fetchNextReview();
      }, 2000);

    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  };

  const getQualityDescription = (score) => {
    const descriptions = {
      0: { text: 'Complete Blackout', color: 'text-red-600', icon: XCircle },
      1: { text: 'Incorrect Response', color: 'text-red-500', icon: XCircle },
      2: { text: 'Incorrect Response', color: 'text-orange-500', icon: XCircle },
      3: { text: 'Correct Response', color: 'text-yellow-500', icon: CheckCircle },
      4: { text: 'Correct Response', color: 'text-green-500', icon: CheckCircle },
      5: { text: 'Perfect Response', color: 'text-green-600', icon: Star }
    };
    return descriptions[score] || descriptions[0];
  };

  const getQualityColor = (score) => {
    const colors = {
      0: 'bg-red-100 border-red-300 text-red-700',
      1: 'bg-red-100 border-red-300 text-red-700',
      2: 'bg-orange-100 border-orange-300 text-orange-700',
      3: 'bg-yellow-100 border-yellow-300 text-yellow-700',
      4: 'bg-green-100 border-green-300 text-green-700',
      5: 'bg-green-100 border-green-300 text-green-700'
    };
    return colors[score] || colors[0];
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-8">
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <span className="ml-3 text-gray-600">Loading review...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-8">
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center">
            <AlertCircle className="w-5 h-5 text-red-400 mr-2" />
            <span className="text-red-700">Error: {error}</span>
          </div>
          <button
            onClick={fetchNextReview}
            className="mt-3 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  if (!currentReview) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-8">
        <div className="text-center">
          <CheckCircle className="w-16 h-16 text-green-500 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-gray-900 mb-2">All caught up!</h3>
          <p className="text-gray-600 mb-6">No reviews due at the moment.</p>
          <button
            onClick={fetchNextReview}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium"
          >
            Check for New Reviews
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-lg p-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          <BookOpen className="w-6 h-6 text-blue-600" />
          <div>
            <h3 className="text-lg font-semibold text-gray-900">{currentReview.topic}</h3>
            <div className="flex items-center space-x-4 text-sm text-gray-600">
              <span>Interval: {currentReview.interval_days} days</span>
              <span>Repetitions: {currentReview.repetitions}</span>
              <span>EF: {currentReview.easiness_factor.toFixed(2)}</span>
            </div>
          </div>
        </div>
        
        {startTime && (
          <div className="flex items-center space-x-2 text-sm text-gray-600">
            <Clock className="w-4 h-4" />
            <span>{Math.floor((Date.now() - startTime) / 1000)}s</span>
          </div>
        )}
      </div>

      {/* Question */}
      <div className="mb-8">
        <h4 className="text-lg font-medium text-gray-900 mb-4">Question:</h4>
        <div className="bg-gray-50 rounded-lg p-6 border-l-4 border-blue-500">
          <p className="text-gray-800 leading-relaxed">
            {currentReview.content?.question || 'Question not available'}
          </p>
        </div>
      </div>

      {/* Answer Section */}
      <AnimatePresence>
        {!showAnswer ? (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="text-center mb-8"
          >
            <button
              onClick={handleShowAnswer}
              className="px-8 py-4 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium text-lg flex items-center space-x-2 mx-auto"
            >
              <span>Show Answer</span>
              <ArrowRight className="w-5 h-5" />
            </button>
          </motion.div>
        ) : (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="mb-8"
          >
            <h4 className="text-lg font-medium text-gray-900 mb-4">Answer:</h4>
            <div className="bg-green-50 rounded-lg p-6 border-l-4 border-green-500">
              <p className="text-gray-800 leading-relaxed">
                {currentReview.content?.answer || 'Answer not available'}
              </p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Quality Selection */}
      <AnimatePresence>
        {showAnswer && !qualityScore && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="mb-8"
          >
            <h4 className="text-lg font-medium text-gray-900 mb-4">
              How well did you know this?
            </h4>
            <div className="grid grid-cols-3 gap-3">
              {[0, 1, 2, 3, 4, 5].map(score => {
                const desc = getQualityDescription(score);
                const Icon = desc.icon;
                return (
                  <motion.button
                    key={score}
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={() => handleQualitySelect(score)}
                    className={`p-4 rounded-lg border-2 transition-all ${getQualityColor(score)}`}
                  >
                    <div className="flex flex-col items-center space-y-2">
                      <Icon className="w-6 h-6" />
                      <span className="font-medium">{score}</span>
                      <span className="text-xs text-center">{desc.text}</span>
                    </div>
                  </motion.button>
                );
              })}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Submission Status */}
      <AnimatePresence>
        {qualityScore !== null && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="text-center"
          >
            {submitting ? (
              <div className="flex items-center justify-center space-x-3">
                <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
                <span className="text-gray-600">Submitting review...</span>
              </div>
            ) : (
              <div className="flex items-center justify-center space-x-3">
                <CheckCircle className="w-6 h-6 text-green-500" />
                <span className="text-green-700 font-medium">Review completed!</span>
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Actions */}
      <div className="mt-8 flex justify-center space-x-4">
        <button
          onClick={fetchNextReview}
          className="px-6 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 font-medium flex items-center space-x-2"
        >
          <RotateCcw className="w-4 h-4" />
          <span>Skip</span>
        </button>
      </div>
    </div>
  );
};

export default ReviewFlow;
