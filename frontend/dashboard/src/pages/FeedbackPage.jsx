import React from 'react';
import { useAuth } from '../contexts/AuthContext';
import FeedbackHistory from '../components/FeedbackHistory';
import { Brain, MessageSquare } from 'lucide-react';

export default function FeedbackPage() {
  const { user, token } = useAuth();

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-4">
              <div className="w-10 h-10 bg-gradient-to-r from-green-600 to-blue-600 rounded-lg flex items-center justify-center">
                <MessageSquare className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Feedback History</h1>
                <p className="text-gray-600">Your personalized learning feedback</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <FeedbackHistory userId={user?.id} token={token} />
      </div>
    </div>
  );
}
