import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { TrendingUp, TrendingDown, Award, Target, Zap, BookOpen } from 'lucide-react';

const LearningDNA = ({ userId, token }) => {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedTopic, setSelectedTopic] = useState(null);
  const [topicHistory, setTopicHistory] = useState(null);

  useEffect(() => {
    fetchLearningDNAProfile();
  }, [userId, token]);

  const fetchLearningDNAProfile = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE_URL}/api/dna/profile/dna/${userId}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error('Failed to fetch Learning DNA profile');
      }

      const data = await response.json();
      setProfile(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const fetchTopicHistory = async (topic) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/dna/profile/topic-history/${userId}/${encodeURIComponent(topic)}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error('Failed to fetch topic history');
      }

      const data = await response.json();
      setTopicHistory(data.mastery_history);
    } catch (err) {
      console.error('Failed to fetch topic history:', err);
    }
  };

  const getMasteryColor = (score) => {
    if (score >= 80) return 'from-green-400 to-green-600';
    if (score >= 60) return 'from-blue-400 to-blue-600';
    if (score >= 40) return 'from-yellow-400 to-yellow-600';
    return 'from-red-400 to-red-600';
  };

  const getMasteryLevel = (score) => {
    if (score >= 85) return 'Expert';
    if (score >= 60) return 'Advanced';
    if (score >= 25) return 'Intermediate';
    return 'Beginner';
  };

  const getMasteryIcon = (level) => {
    switch (level) {
      case 'Expert': return '🎯';
      case 'Advanced': return '🚀';
      case 'Intermediate': return '📈';
      default: return '🌱';
    }
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-6">
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <span className="ml-2 text-gray-600">Loading Learning DNA...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return null; // Don't render anything if there's an error
  }

  if (!profile) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-6">
        <div className="text-center text-gray-500">
          <BookOpen className="w-12 h-12 mx-auto mb-4 text-gray-400" />
          <h3 className="text-lg font-semibold mb-2">No Learning Data Yet</h3>
          <p className="text-sm">Complete some lessons to see your Learning DNA profile!</p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 bg-gradient-to-r from-purple-600 to-blue-600 rounded-lg flex items-center justify-center">
            <Target className="w-6 h-6 text-white" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-gray-900">Learning DNA</h2>
            <p className="text-sm text-gray-600">Your learning profile & mastery</p>
          </div>
        </div>
        <button
          onClick={fetchLearningDNAProfile}
          className="text-blue-600 hover:text-blue-800 text-sm font-medium"
        >
          Refresh
        </button>
      </div>

      {/* Overall Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-gradient-to-r from-blue-50 to-blue-100 rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-blue-600 font-medium">Total Topics</p>
              <p className="text-2xl font-bold text-blue-800">{profile.total_topics}</p>
            </div>
            <BookOpen className="w-8 h-8 text-blue-500" />
          </div>
        </div>
        
        <div className="bg-gradient-to-r from-green-50 to-green-100 rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-green-600 font-medium">Avg Mastery</p>
              <p className="text-2xl font-bold text-green-800">{profile.average_mastery.toFixed(1)}%</p>
            </div>
            <Target className="w-8 h-8 text-green-500" />
          </div>
        </div>
        
        <div className="bg-gradient-to-r from-purple-50 to-purple-100 rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-purple-600 font-medium">Strengths</p>
              <p className="text-2xl font-bold text-purple-800">{profile.strengths.length}</p>
            </div>
            <TrendingUp className="w-8 h-8 text-purple-500" />
          </div>
        </div>
        
        <div className="bg-gradient-to-r from-orange-50 to-orange-100 rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-orange-600 font-medium">Improving</p>
              <p className="text-2xl font-bold text-orange-800">{profile.improving_topics.length}</p>
            </div>
            <Zap className="w-8 h-8 text-orange-500" />
          </div>
        </div>
      </div>

      {/* Topic Mastery Bars */}
      <div className="mb-6">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">Topic Mastery</h3>
        <div className="space-y-3">
          {profile.topic_mastery.map((topic, index) => (
            <motion.div
              key={topic.topic}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
              className="bg-gray-50 rounded-lg p-4 hover:bg-gray-100 transition-colors cursor-pointer"
              onClick={() => {
                setSelectedTopic(topic.topic);
                fetchTopicHistory(topic.topic);
              }}
            >
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center space-x-2">
                  <span className="text-lg">{getMasteryIcon(topic.level)}</span>
                  <span className="font-medium text-gray-800">{topic.topic}</span>
                  <span className="text-sm text-gray-500">({topic.level})</span>
                </div>
                <div className="flex items-center space-x-2">
                  <span className="text-sm font-semibold text-gray-700">
                    {topic.score.toFixed(1)}%
                  </span>
                  {topic.streak > 0 && (
                    <div className="flex items-center space-x-1 bg-orange-100 text-orange-700 px-2 py-1 rounded-full">
                      <Zap className="w-3 h-3" />
                      <span className="text-xs font-medium">{topic.streak}</span>
                    </div>
                  )}
                </div>
              </div>
              
              <div className="relative">
                <div className="w-full bg-gray-200 rounded-full h-3">
                  <motion.div
                    className={`h-3 rounded-full bg-gradient-to-r ${getMasteryColor(topic.score)}`}
                    initial={{ width: 0 }}
                    animate={{ width: `${topic.score}%` }}
                    transition={{ duration: 1, delay: index * 0.1 }}
                  />
                </div>
                <div className="flex justify-between text-xs text-gray-500 mt-1">
                  <span>0%</span>
                  <span>100%</span>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Strengths & Weaknesses */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        {/* Strengths */}
        <div className="bg-green-50 rounded-lg p-4">
          <h4 className="text-lg font-semibold text-green-800 mb-3 flex items-center">
            <TrendingUp className="w-5 h-5 mr-2" />
            Strengths
          </h4>
          {profile.strengths.length > 0 ? (
            <div className="space-y-2">
              {profile.strengths.map((strength, index) => (
                <motion.div
                  key={strength.topic}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="flex items-center justify-between bg-white rounded-lg p-3"
                >
                  <span className="font-medium text-gray-800">{strength.topic}</span>
                  <div className="flex items-center space-x-2">
                    <span className="text-sm font-semibold text-green-600">
                      {strength.score.toFixed(1)}%
                    </span>
                    {strength.streak > 0 && (
                      <span className="text-xs bg-orange-100 text-orange-700 px-2 py-1 rounded-full">
                        🔥 {strength.streak}
                      </span>
                    )}
                  </div>
                </motion.div>
              ))}
            </div>
          ) : (
            <p className="text-green-600 text-sm">Keep learning to build your strengths!</p>
          )}
        </div>

        {/* Weaknesses */}
        <div className="bg-red-50 rounded-lg p-4">
          <h4 className="text-lg font-semibold text-red-800 mb-3 flex items-center">
            <TrendingDown className="w-5 h-5 mr-2" />
            Areas to Improve
          </h4>
          {profile.weaknesses.length > 0 ? (
            <div className="space-y-2">
              {profile.weaknesses.map((weakness, index) => (
                <motion.div
                  key={weakness.topic}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="flex items-center justify-between bg-white rounded-lg p-3"
                >
                  <span className="font-medium text-gray-800">{weakness.topic}</span>
                  <div className="flex items-center space-x-2">
                    <span className="text-sm font-semibold text-red-600">
                      {weakness.score.toFixed(1)}%
                    </span>
                    <span className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded-full">
                      {weakness.attempts} attempts
                    </span>
                  </div>
                </motion.div>
              ))}
            </div>
          ) : (
            <p className="text-red-600 text-sm">Great job! No major weaknesses detected.</p>
          )}
        </div>
      </div>

      {/* Recent Badges */}
      {profile.recent_badges.length > 0 && (
        <div className="mb-6">
          <h4 className="text-lg font-semibold text-gray-800 mb-3 flex items-center">
            <Award className="w-5 h-5 mr-2" />
            Recent Achievements
          </h4>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            {profile.recent_badges.map((badge, index) => (
              <motion.div
                key={badge.name}
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: index * 0.1 }}
                className="bg-gradient-to-r from-yellow-50 to-orange-50 border border-yellow-200 rounded-lg p-3"
              >
                <div className="flex items-center space-x-2">
                  <span className="text-lg">{badge.name}</span>
                </div>
                <p className="text-xs text-gray-600 mt-1">{badge.description}</p>
                {badge.topic && (
                  <p className="text-xs text-blue-600 mt-1">Topic: {badge.topic}</p>
                )}
              </motion.div>
            ))}
          </div>
        </div>
      )}

      {/* Learning Velocity */}
      <div className="bg-blue-50 rounded-lg p-4">
        <h4 className="text-lg font-semibold text-blue-800 mb-3">Learning Velocity</h4>
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <span className="text-sm text-blue-600">Trend:</span>
            <span className={`text-sm font-semibold ${
              profile.learning_velocity.trend === 'accelerating' ? 'text-green-600' :
              profile.learning_velocity.trend === 'declining' ? 'text-red-600' :
              'text-gray-600'
            }`}>
              {profile.learning_velocity.trend === 'accelerating' ? '📈 Accelerating' :
               profile.learning_velocity.trend === 'declining' ? '📉 Declining' :
               '📊 Stable'}
            </span>
          </div>
          <div className="flex items-center space-x-2">
            <span className="text-sm text-blue-600">Velocity:</span>
            <span className="text-sm font-semibold text-blue-800">
              {profile.learning_velocity.velocity.toFixed(2)}
            </span>
          </div>
          <div className="flex items-center space-x-2">
            <span className="text-sm text-blue-600">Topics Tracked:</span>
            <span className="text-sm font-semibold text-blue-800">
              {profile.learning_velocity.topics_tracked}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LearningDNA;
