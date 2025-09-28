import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { useAuth } from '../contexts/AuthContext';
import { useRevision } from '../hooks/useRevision';
import RevisionCalendar from '../components/RevisionCalendar';
import ReviewFlow from '../components/ReviewFlow';
import DueNowPanel from '../components/DueNowPanel';
import { Calendar, BookOpen, BarChart3, Clock } from 'lucide-react';

export default function RevisionPage() {
  const { user, token } = useAuth();
  const { 
    dueReviews, 
    stats, 
    insights, 
    loading, 
    error,
    fetchStats,
    fetchInsights 
  } = useRevision(user?.id, token);
  
  const [activeTab, setActiveTab] = useState('calendar');

  const tabs = [
    { id: 'calendar', label: 'Calendar', icon: Calendar },
    { id: 'reviews', label: 'Due Reviews', icon: BookOpen },
    { id: 'stats', label: 'Statistics', icon: BarChart3 },
    { id: 'flow', label: 'Review Flow', icon: Clock }
  ];

  const handleReviewComplete = (result) => {
    console.log('Review completed:', result);
    // Refresh stats after completion
    fetchStats();
    fetchInsights();
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Revision Center</h1>
              <p className="text-gray-600 mt-1">Manage your spaced repetition schedule</p>
            </div>
            
            {/* Quick Stats */}
            <div className="flex items-center space-x-6">
              <div className="text-center">
                <div className="text-2xl font-bold text-red-600">{dueReviews.filter(r => r.overdue_days > 0).length}</div>
                <div className="text-sm text-gray-600">Overdue</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-orange-600">{dueReviews.filter(r => r.overdue_days === 0).length}</div>
                <div className="text-sm text-gray-600">Due Today</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">{stats?.total_schedules || 0}</div>
                <div className="text-sm text-gray-600">Total Items</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Tab Navigation */}
        <div className="mb-8">
          <div className="border-b border-gray-200">
            <nav className="-mb-px flex space-x-8">
              {tabs.map((tab) => {
                const Icon = tab.icon;
                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`flex items-center space-x-2 py-2 px-1 border-b-2 font-medium text-sm ${
                      activeTab === tab.id
                        ? 'border-blue-500 text-blue-600'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    }`}
                  >
                    <Icon className="w-4 h-4" />
                    <span>{tab.label}</span>
                  </button>
                );
              })}
            </nav>
          </div>
        </div>

        {/* Tab Content */}
        <motion.div
          key={activeTab}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
        >
          {activeTab === 'calendar' && (
            <RevisionCalendar userId={user?.id} token={token} />
          )}

          {activeTab === 'reviews' && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              <DueNowPanel userId={user?.id} token={token} />
              
              {/* Additional Review Info */}
              <div className="bg-white rounded-lg shadow-lg p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Review Insights</h3>
                
                {insights && insights.insights ? (
                  <div className="space-y-3">
                    {insights.insights.map((insight, index) => (
                      <div key={index} className="p-3 bg-blue-50 rounded-lg border-l-4 border-blue-400">
                        <p className="text-sm text-blue-800">{insight}</p>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-gray-600 text-sm">Complete more reviews to see insights.</p>
                )}
              </div>
            </div>
          )}

          {activeTab === 'stats' && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              {/* Statistics Cards */}
              <div className="space-y-6">
                <div className="bg-white rounded-lg shadow-lg p-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Overview</h3>
                  {stats ? (
                    <div className="space-y-4">
                      <div className="flex justify-between">
                        <span className="text-gray-600">Total Schedules:</span>
                        <span className="font-medium">{stats.total_schedules}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Due Now:</span>
                        <span className="font-medium text-orange-600">{stats.due_now}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Overdue:</span>
                        <span className="font-medium text-red-600">{stats.overdue}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Avg. Easiness Factor:</span>
                        <span className="font-medium">{stats.average_easiness_factor}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Recent Activity:</span>
                        <span className="font-medium">{stats.recent_activity} reviews</span>
                      </div>
                    </div>
                  ) : (
                    <p className="text-gray-600">No statistics available.</p>
                  )}
                </div>

                {/* Topic Distribution */}
                {stats && stats.topic_distribution && (
                  <div className="bg-white rounded-lg shadow-lg p-6">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">Topic Distribution</h3>
                    <div className="space-y-2">
                      {Object.entries(stats.topic_distribution).map(([topic, count]) => (
                        <div key={topic} className="flex justify-between items-center">
                          <span className="text-gray-600">{topic}</span>
                          <span className="font-medium">{count}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {/* Emotion Insights */}
              <div className="bg-white rounded-lg shadow-lg p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Emotion Insights</h3>
                {insights && insights.emotion_counts ? (
                  <div className="space-y-4">
                    <div>
                      <h4 className="font-medium text-gray-700 mb-2">Emotion Frequency</h4>
                      <div className="space-y-2">
                        {Object.entries(insights.emotion_counts).map(([emotion, count]) => (
                          <div key={emotion} className="flex justify-between items-center">
                            <span className="text-gray-600 capitalize">{emotion}</span>
                            <span className="font-medium">{count}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                    
                    {insights.average_performance && (
                      <div>
                        <h4 className="font-medium text-gray-700 mb-2">Performance by Emotion</h4>
                        <div className="space-y-2">
                          {Object.entries(insights.average_performance).map(([emotion, score]) => (
                            <div key={emotion} className="flex justify-between items-center">
                              <span className="text-gray-600 capitalize">{emotion}</span>
                              <span className="font-medium">{score.toFixed(2)}/5</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                ) : (
                  <p className="text-gray-600 text-sm">Complete reviews with emotion detection to see insights.</p>
                )}
              </div>
            </div>
          )}

          {activeTab === 'flow' && (
            <ReviewFlow 
              userId={user?.id} 
              token={token} 
              onComplete={handleReviewComplete}
            />
          )}
        </motion.div>
      </div>
    </div>
  );
}
