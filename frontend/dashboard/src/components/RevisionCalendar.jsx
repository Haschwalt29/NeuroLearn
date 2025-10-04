import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Calendar, ChevronLeft, ChevronRight, Clock, BookOpen, AlertCircle } from 'lucide-react';

const RevisionCalendar = ({ userId, token }) => {
  const [currentDate, setCurrentDate] = useState(new Date());
  const [calendarData, setCalendarData] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedDate, setSelectedDate] = useState(null);

  useEffect(() => {
    fetchCalendarData();
  }, [currentDate, userId, token]);

  const fetchCalendarData = async () => {
    try {
      setLoading(true);
      setError(null);

      const startDate = new Date(currentDate);
      startDate.setDate(1);
      const endDate = new Date(currentDate);
      endDate.setMonth(endDate.getMonth() + 1);
      endDate.setDate(0);

      const response = await fetch(
        `/api/revision/calendar?start=${startDate.toISOString()}&end=${endDate.toISOString()}`,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );

      if (!response.ok) {
        throw new Error('Failed to fetch calendar data');
      }

      const data = await response.json();
      setCalendarData(data.calendar || {});
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const navigateMonth = (direction) => {
    setCurrentDate(prev => {
      const newDate = new Date(prev);
      if (direction === 'prev') {
        newDate.setMonth(newDate.getMonth() - 1);
      } else {
        newDate.setMonth(newDate.getMonth() + 1);
      }
      return newDate;
    });
  };

  const getDaysInMonth = (date) => {
    const year = date.getFullYear();
    const month = date.getMonth();
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const daysInMonth = lastDay.getDate();
    const startingDayOfWeek = firstDay.getDay();

    const days = [];
    
    for (let i = 0; i < startingDayOfWeek; i++) {
      days.push(null);
    }
    for (let day = 1; day <= daysInMonth; day++) {
      days.push(new Date(year, month, day));
    }
    
    return days;
  };

  const getReviewsForDate = (date) => {
    if (!date) return [];
    const dateStr = date.toISOString().split('T')[0];
    return calendarData[dateStr] || [];
  };

  const getDateStatus = (date) => {
    if (!date) return 'empty';
    
    const today = new Date();
    const dateStr = date.toISOString().split('T')[0];
    const reviews = calendarData[dateStr] || [];
    
    if (date < today) return 'past';
    if (date.toDateString() === today.toDateString()) return 'today';
    if (reviews.length > 0) return 'has-reviews';
    return 'future';
  };

  const startReview = (review) => {
    console.log('Starting review:', review);
    alert(`Starting review for: ${review.topic}`);
  };

  const monthNames = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
  ];

  const dayNames = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-6">
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <span className="ml-3 text-gray-600">Loading calendar...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return null; // Don't render anything if there's an error
  }

  const days = getDaysInMonth(currentDate);

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-2">
          <Calendar className="w-5 h-5 text-blue-600" />
          <h3 className="text-lg font-semibold text-gray-900">Revision Calendar</h3>
        </div>
        
        <div className="flex items-center space-x-2">
          <button
            onClick={() => navigateMonth('prev')}
            className="p-2 hover:bg-gray-100 rounded-lg"
          >
            <ChevronLeft className="w-4 h-4" />
          </button>
          <span className="text-lg font-medium text-gray-900 min-w-[140px] text-center">
            {monthNames[currentDate.getMonth()]} {currentDate.getFullYear()}
          </span>
          <button
            onClick={() => navigateMonth('next')}
            className="p-2 hover:bg-gray-100 rounded-lg"
          >
            <ChevronRight className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Calendar Grid */}
      <div className="grid grid-cols-7 gap-1 mb-4">
        {dayNames.map(day => (
          <div key={day} className="text-center text-sm font-medium text-gray-500 py-2">
            {day}
          </div>
        ))}
      </div>

      <div className="grid grid-cols-7 gap-1">
        {days.map((day, index) => {
          const status = getDateStatus(day);
          const reviews = getReviewsForDate(day);
          
          return (
            <motion.div
              key={index}
              className={`
                aspect-square p-2 rounded-lg cursor-pointer transition-all
                ${status === 'empty' ? 'bg-transparent' : ''}
                ${status === 'past' ? 'bg-gray-100 text-gray-400' : ''}
                ${status === 'today' ? 'bg-blue-100 text-blue-900 border-2 border-blue-300' : ''}
                ${status === 'has-reviews' ? 'bg-green-50 text-green-900 hover:bg-green-100' : ''}
                ${status === 'future' ? 'bg-white text-gray-700 hover:bg-gray-50' : ''}
              `}
              onClick={() => day && setSelectedDate(day)}
              whileHover={{ scale: day ? 1.05 : 1 }}
            >
              {day && (
                <div className="h-full flex flex-col">
                  <span className="text-sm font-medium">{day.getDate()}</span>
                  {reviews.length > 0 && (
                    <div className="flex-1 flex items-center justify-center">
                      <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                    </div>
                  )}
                </div>
              )}
            </motion.div>
          );
        })}
      </div>

      {/* Selected Date Details */}
      {selectedDate && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mt-6 p-4 bg-gray-50 rounded-lg"
        >
          <h4 className="font-medium text-gray-900 mb-3">
            Reviews for {selectedDate.toLocaleDateString()}
          </h4>
          
          {getReviewsForDate(selectedDate).length === 0 ? (
            <p className="text-gray-600 text-sm">No reviews scheduled for this date.</p>
          ) : (
            <div className="space-y-2">
              {getReviewsForDate(selectedDate).map((review, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="flex items-center justify-between p-3 bg-white rounded-lg border"
                >
                  <div className="flex items-center space-x-3">
                    <BookOpen className="w-4 h-4 text-blue-600" />
                    <div>
                      <h5 className="font-medium text-gray-900">{review.topic}</h5>
                      <p className="text-sm text-gray-600">
                        {review.time} • {review.repetitions} reps
                      </p>
                    </div>
                  </div>
                  
                  <button
                    onClick={() => startReview(review)}
                    className="px-3 py-1 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700"
                  >
                    Start Review
                  </button>
                </motion.div>
              ))}
            </div>
          )}
        </motion.div>
      )}

      {/* Legend */}
      <div className="mt-6 flex items-center justify-center space-x-6 text-sm text-gray-600">
        <div className="flex items-center space-x-2">
          <div className="w-3 h-3 bg-blue-100 border border-blue-300 rounded"></div>
          <span>Today</span>
        </div>
        <div className="flex items-center space-x-2">
          <div className="w-3 h-3 bg-green-50 rounded"></div>
          <span>Has Reviews</span>
        </div>
        <div className="flex items-center space-x-2">
          <div className="w-3 h-3 bg-gray-100 rounded"></div>
          <span>Past</span>
        </div>
      </div>
    </div>
  );
};

export default RevisionCalendar;
