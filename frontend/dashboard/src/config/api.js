// API Configuration
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || ''

export const API_ENDPOINTS = {
  // Auth endpoints
  AUTH: {
    LOGIN: '/api/auth/login',
    SIGNUP: '/api/auth/signup',
    ME: '/api/auth/me',
  },
  
  // Learning DNA endpoints
  DNA: {
    PROFILE: (userId) => `/api/dna/profile/dna/${userId}`,
    UPDATE: '/api/dna/profile/update',
    MASTERY: (userId) => `/api/dna/profile/mastery/${userId}`,
    PROGRESS: (userId, params = '') => `/api/dna/profile/progress/${userId}?${params}`,
    TOPIC_HISTORY: (userId, topic, days = 30) => `/api/dna/profile/topic-history/${userId}/${encodeURIComponent(topic)}?days=${days}`,
    BADGES: (userId) => `/api/dna/badges/${userId}`,
    STATS: (userId) => `/api/dna/stats/${userId}`,
    LEADERBOARD: '/api/dna/leaderboard',
  },
  
  // Learning Style endpoints
  LEARNING_STYLE: {
    BASE: '/api/learning-style/',
    UPDATE: '/api/learning-style/update',
    INSIGHTS: '/api/learning-style/insights',
    RECOMMENDATIONS: '/api/learning-style/recommendations',
    STATS: '/api/learning-style/stats',
    RESET: '/api/learning-style/reset',
  },
  
  // Revision endpoints
  REVISION: {
    DUE: (params = '') => `/api/revision/due?${params}`,
    CALENDAR: (params = '') => `/api/revision/calendar?${params}`,
    STATS: '/api/revision/stats',
    INSIGHTS: '/api/revision/insights',
    COMPLETE: '/api/revision/complete',
    SNOOZE: '/api/revision/snooze',
    SCHEDULE: '/api/revision/schedule',
    SCHEDULE_BY_ID: (contentId) => `/api/revision/schedule/${contentId}`,
  },
  
  // Feedback endpoints
  FEEDBACK: {
    GENERATE: '/api/feedback/generate',
    LESSON_COMPLETE: '/api/feedback/lesson/complete',
    QUIZ_COMPLETE: '/api/feedback/quiz/complete',
    HISTORY: (limit = 10) => `/api/feedback/history?limit=${limit}`,
    LATEST: '/api/feedback/latest',
    STATS: '/api/feedback/stats',
    MILESTONE: (milestoneType) => `/api/feedback/milestone/${milestoneType}`,
  },
  
  // Gamification endpoints
  GAMIFICATION: {
    STATUS: '/api/gamification/status',
  },
  
  // Quest endpoints
  QUESTS: {
    ACTIVE: '/api/quests/active',
    BY_ID: (id) => `/api/quests/${id}`,
  },
  
  // Personalization endpoints
  PERSONALIZATION: {
    INSIGHTS: '/api/personalization/insights',
    CUSTOM_EXERCISES: '/api/personalization/custom-exercises',
  },
}

export default API_ENDPOINTS
