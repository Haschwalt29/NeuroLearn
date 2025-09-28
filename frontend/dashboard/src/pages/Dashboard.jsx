import React, { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { useAuth } from '../contexts/AuthContext'
import { useEmotion } from '../contexts/EmotionContext'
import { useSocket } from '../contexts/SocketContext'
import MoodIndicator from '../components/MoodIndicator'
import EmotionTimeline from '../components/EmotionTimeline'
import LearningProgress from '../components/LearningProgress'
import AdaptiveContent from '../components/AdaptiveContent'
import Achievements from '../components/Achievements'
import StatsCards from '../components/StatsCards'
import FeedbackCard from '../components/FeedbackCard'
import LearningDNA from '../components/LearningDNA'
import LearningStyleCard from '../components/LearningStyleCard'
import DueNowPanel from '../components/DueNowPanel'
import RevisionCalendar from '../components/RevisionCalendar'
import ReviewFlow from '../components/ReviewFlow'
import XPLevelBar from '../components/XPLevelBar'
import BadgeModal from '../components/BadgeModal'
import StreakIndicator from '../components/StreakIndicator'
import QuestBoard from '../components/QuestBoard'
import LearningInsights from '../components/LearningInsights'
import CustomExercises from '../components/CustomExercises'
import LiveEmotionDetector from '../components/LiveEmotionDetector'
// import DevSettings from '../components/DevSettings'
import StoryDashboard from '../components/StoryDashboard'
import RewardsPopup from '../components/RewardsPopup'
import CodingSandbox from '../components/CodingSandbox'
import KnowledgeGraph from '../components/KnowledgeGraph'
import { useFeedback } from '../hooks/useFeedback'
import { useRevision } from '../hooks/useRevision'
import { useStory } from '../hooks/useStory'
import { Brain, BookOpen, Trophy, Target, Award, Flame, Sword, GraduationCap, Bell, MessageCircle, Sparkles, TrendingUp, Users, Clock } from 'lucide-react'
import VisualizationLab from './VisualizationLab'
import CoLearnerWidget from '../components/colearner/CoLearnerWidget'
import CoLearnerPanel from '../components/colearner/CoLearnerPanel'
import { useCoLearner } from '../hooks/useCoLearner'
import FreshLessons from '../components/curriculum/FreshLessons'
import AdaptivePath from '../components/curriculum/AdaptivePath'
import CurriculumUpdates from '../components/curriculum/CurriculumUpdates'
// import DebatePanel from '../components/debate/DebatePanel'
// import DebateHistory from '../components/debate/DebateHistory'
import { PageTransition, CardTransition, StaggerContainer, FadeIn, ModalTransition } from '../components/common/TransitionWrapper'

export default function Dashboard() {
  const { user, token } = useAuth()
  const { currentEmotion, isCapturing, startCapture, stopCapture } = useEmotion()
  const { connected } = useSocket()
  const { currentFeedback, clearCurrentFeedback, generateFeedback } = useFeedback(token)
  const { dueReviews, stats: revisionStats, overdueCount, dueTodayCount } = useRevision(user?.id, token)
  const { storyData, rewards, showRewards, closeRewards } = useStory(token)
  const { mirrorEmotion } = useCoLearner(token)
  const [stats, setStats] = useState({
    totalStudyTime: 0,
    lessonsCompleted: 0,
    currentStreak: 0,
    achievements: 0
  })
  const [showReviewFlow, setShowReviewFlow] = useState(false)
  const [showBadgeModal, setShowBadgeModal] = useState(false)
  const [activeTab, setActiveTab] = useState('overview')
  const [showEmotionDetector, setShowEmotionDetector] = useState(true)
  const [showCoPanel, setShowCoPanel] = useState(false)
  // const [showDebatePanel, setShowDebatePanel] = useState(false)

  useEffect(() => {
    // Load user stats (mock data for now)
    setStats({
      totalStudyTime: 120, // minutes
      lessonsCompleted: 15,
      currentStreak: 7,
      achievements: 3
    })
  }, [])

  // Mirror emotions to co-learner
  useEffect(() => {
    if (currentEmotion && currentEmotion.emotion) {
      try {
        mirrorEmotion(currentEmotion.emotion, currentEmotion.confidence)
      } catch (error) {
        console.warn('Failed to mirror emotion to co-learner:', error)
      }
    }
  }, [currentEmotion, mirrorEmotion])

  const handleEmotionToggle = () => {
    if (isCapturing) {
      stopCapture()
    } else {
      startCapture()
    }
  }

  const handleGenerateFeedback = async () => {
    try {
      await generateFeedback()
    } catch (error) {
      console.error('Failed to generate feedback:', error)
    }
  }

  const handleStartReview = () => {
    setShowReviewFlow(true)
  }

  const handleReviewComplete = (result) => {
    console.log('Review completed:', result)
    setShowReviewFlow(false)
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors duration-300">
      <PageTransition>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {user ? (
            <div className="space-y-8">
              {/* Welcome Header */}
              <FadeIn delay={0.1}>
                <div className="text-center mb-12">
                  <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-4">
                    Welcome back, {user.name?.split(' ')[0]}! 👋
                  </h1>
                  <p className="text-lg text-gray-600 dark:text-gray-300">
                    Ready to continue your learning journey?
                  </p>
                  <div className="flex items-center justify-center gap-2 mt-4">
                    <div className={`w-3 h-3 rounded-full ${connected ? 'bg-green-500' : 'bg-red-500'}`} />
                    <span className="text-sm text-gray-600 dark:text-gray-400">
                      {connected ? 'Connected' : 'Disconnected'}
                    </span>
                  </div>
                </div>
              </FadeIn>

              {/* Quick Actions */}
              <StaggerContainer>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                  <CardTransition delay={0.1}>
                    <motion.button
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                      onClick={handleGenerateFeedback}
                      className="w-full p-6 bg-gradient-to-r from-green-500 to-emerald-600 rounded-2xl text-white shadow-lg hover:shadow-xl transition-all duration-200"
                    >
                      <div className="flex items-center gap-3">
                        <div className="p-2 bg-white/20 rounded-xl">
                          <Award className="w-6 h-6" />
                        </div>
                        <div className="text-left">
                          <h3 className="font-semibold text-lg">Get Feedback</h3>
                          <p className="text-sm opacity-90">Analyze your progress</p>
                        </div>
                      </div>
                    </motion.button>
                  </CardTransition>

                  <CardTransition delay={0.2}>
                    <motion.button
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                      onClick={() => setShowBadgeModal(true)}
                      className="w-full p-6 bg-gradient-to-r from-yellow-500 to-orange-500 rounded-2xl text-white shadow-lg hover:shadow-xl transition-all duration-200"
                    >
                      <div className="flex items-center gap-3">
                        <div className="p-2 bg-white/20 rounded-xl">
                          <Trophy className="w-6 h-6" />
                        </div>
                        <div className="text-left">
                          <h3 className="font-semibold text-lg">View Badges</h3>
                          <p className="text-sm opacity-90">See your achievements</p>
                        </div>
                      </div>
                    </motion.button>
                  </CardTransition>

                  <CardTransition delay={0.3}>
                    <motion.button
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                      onClick={handleStartReview}
                      className="w-full p-6 bg-gradient-to-r from-purple-500 to-pink-500 rounded-2xl text-white shadow-lg hover:shadow-xl transition-all duration-200"
                    >
                      <div className="flex items-center gap-3">
                        <div className="p-2 bg-white/20 rounded-xl">
                          <BookOpen className="w-6 h-6" />
                        </div>
                        <div className="text-left">
                          <h3 className="font-semibold text-lg">Start Review</h3>
                          <p className="text-sm opacity-90">Practice with spaced repetition</p>
                        </div>
                      </div>
                    </motion.button>
                  </CardTransition>
                </div>
              </StaggerContainer>

              {/* Tab Navigation */}
              <CardTransition delay={0.4}>
                <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg border border-gray-200 dark:border-gray-700 overflow-hidden">
                  <div className="border-b border-gray-200 dark:border-gray-700">
                    <div className="flex space-x-1 p-2 overflow-x-auto">
                      <motion.button
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                        onClick={() => setActiveTab('overview')}
                        className={`flex-1 py-3 px-4 rounded-xl text-sm font-medium transition-all duration-200 ${
                          activeTab === 'overview'
                            ? 'bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300 shadow-sm'
                            : 'text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-gray-700'
                        }`}
                      >
                        <Brain className="w-4 h-4 inline mr-2" />
                        Overview
                      </motion.button>
                      <motion.button
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                        onClick={() => setActiveTab('gamification')}
                        className={`flex-1 py-3 px-4 rounded-xl text-sm font-medium transition-all duration-200 ${
                          activeTab === 'gamification'
                            ? 'bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300 shadow-sm'
                            : 'text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-gray-700'
                        }`}
                      >
                        <Trophy className="w-4 h-4 inline mr-2" />
                        Gamification
                      </motion.button>
                      <motion.button
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                        onClick={() => setActiveTab('quests')}
                        className={`flex-1 py-3 px-4 rounded-xl text-sm font-medium transition-all duration-200 ${
                          activeTab === 'quests'
                            ? 'bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300 shadow-sm'
                            : 'text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-gray-700'
                        }`}
                      >
                        <Sword className="w-4 h-4 inline mr-2" />
                        Quests
                      </motion.button>
                      <motion.button
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                        onClick={() => setActiveTab('story')}
                        className={`flex-1 py-3 px-4 rounded-xl text-sm font-medium transition-all duration-200 ${
                          activeTab === 'story'
                            ? 'bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300 shadow-sm'
                            : 'text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-gray-700'
                        }`}
                      >
                        <BookOpen className="w-4 h-4 inline mr-2" />
                        Story
                      </motion.button>
                      <motion.button
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                        onClick={() => setActiveTab('insights')}
                        className={`flex-1 py-3 px-4 rounded-xl text-sm font-medium transition-all duration-200 ${
                          activeTab === 'insights'
                            ? 'bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300 shadow-sm'
                            : 'text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-gray-700'
                        }`}
                      >
                        <Target className="w-4 h-4 inline mr-2" />
                        Insights
                      </motion.button>
                      <motion.button
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                        onClick={() => setActiveTab('coding')}
                        className={`flex-1 py-3 px-4 rounded-xl text-sm font-medium transition-all duration-200 ${
                          activeTab === 'coding'
                            ? 'bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300 shadow-sm'
                            : 'text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-gray-700'
                        }`}
                      >
                        Coding
                      </motion.button>
                      <motion.button
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                        onClick={() => setActiveTab('lab')}
                        className={`flex-1 py-3 px-4 rounded-xl text-sm font-medium transition-all duration-200 ${
                          activeTab === 'lab'
                            ? 'bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300 shadow-sm'
                            : 'text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-gray-700'
                        }`}
                      >
                        3D Lab
                      </motion.button>
                      <motion.button
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                        onClick={() => setActiveTab('curriculum')}
                        className={`flex-1 py-3 px-4 rounded-xl text-sm font-medium transition-all duration-200 ${
                          activeTab === 'curriculum'
                            ? 'bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300 shadow-sm'
                            : 'text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-gray-700'
                        }`}
                      >
                        <GraduationCap className="w-4 h-4 inline mr-2" />
                        Curriculum
                      </motion.button>
                      <motion.button
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                        onClick={() => setActiveTab('updates')}
                        className={`flex-1 py-3 px-4 rounded-xl text-sm font-medium transition-all duration-200 ${
                          activeTab === 'updates'
                            ? 'bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300 shadow-sm'
                            : 'text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-gray-700'
                        }`}
                      >
                        <Bell className="w-4 h-4 inline mr-2" />
                        Updates
                      </motion.button>
                      {/* <motion.button
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                        onClick={() => setActiveTab('debate')}
                        className={`flex-1 py-3 px-4 rounded-xl text-sm font-medium transition-all duration-200 ${
                          activeTab === 'debate'
                            ? 'bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300 shadow-sm'
                            : 'text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-gray-700'
                        }`}
                      >
                        <MessageCircle className="w-4 h-4 inline mr-2" />
                        Debate
                      </motion.button> */}
                  </div>
                  </div>
                  
                  {/* Tab Content */}
                  <div className="p-6">
                  {activeTab === 'overview' && (
                    <StaggerContainer>
                      <div className="space-y-8">
                        {/* Live Emotion Detector - Development Tool */}
                        {showEmotionDetector && (
                          <CardTransition delay={0.1}>
                            <div className="bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20 rounded-2xl p-6 border-2 border-blue-200 dark:border-blue-700">
                              <div className="flex items-center gap-3 mb-4">
                                <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
                                <h2 className="text-lg font-semibold text-gray-800 dark:text-white">🔧 Development Mode - Live Emotion Detection</h2>
                              </div>
                              <LiveEmotionDetector 
                                onEmotionDetected={(emotionData) => {
                                  console.log('Emotion detected:', emotionData);
                                  // Update the EmotionContext to sync with MoodIndicator
                                  // This will help keep both components in sync
                                }}
                                isEnabled={true}
                              />
                            </div>
                          </CardTransition>
                        )}

                        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                          {/* Left Column */}
                          <div className="lg:col-span-2 space-y-8">
                            {/* Stats Cards */}
                            <CardTransition delay={0.2}>
                              <StatsCards stats={stats} />
                            </CardTransition>
                          
                            {/* Adaptive Content */}
                            <CardTransition delay={0.3}>
                              <AdaptiveContent currentEmotion={currentEmotion} userId={user?.id} token={token} />
                            </CardTransition>
                            
                            {/* Learning Progress */}
                            <CardTransition delay={0.4}>
                              <LearningProgress />
                            </CardTransition>
                            
                            {/* Learning DNA */}
                            <CardTransition delay={0.5}>
                              <LearningDNA userId={user?.id} token={token} />
                            </CardTransition>
                            
                            {/* Learning Style */}
                            <CardTransition delay={0.6}>
                              <LearningStyleCard userId={user?.id} token={token} />
                            </CardTransition>
                          </div>

                          {/* Right Column */}
                          <div className="space-y-8">
                            {/* Due Reviews Panel */}
                            <CardTransition delay={0.3}>
                              <DueNowPanel userId={user?.id} token={token} />
                            </CardTransition>
                            
                            {/* Mood Indicator */}
                            <CardTransition delay={0.4}>
                              <MoodIndicator 
                                currentEmotion={currentEmotion} 
                                isCapturing={isCapturing}
                                onStartCapture={startCapture}
                                onStopCapture={stopCapture}
                              />
                            </CardTransition>
                            
                            {/* Emotion Timeline */}
                            <CardTransition delay={0.5}>
                              <EmotionTimeline userId={user?.id} token={token} />
                            </CardTransition>
                            
                            {/* Achievements */}
                            <CardTransition delay={0.6}>
                              <Achievements userId={user?.id} token={token} />
                            </CardTransition>
                          </div>
                        </div>
                      </div>
                    </StaggerContainer>
                  )}

                  {activeTab === 'gamification' && (
                    <StaggerContainer>
                      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                        {/* XP Level Bar */}
                        <CardTransition delay={0.1}>
                          <XPLevelBar userId={user?.id} token={token} />
                        </CardTransition>
                        
                        {/* Streak Indicator */}
                        <CardTransition delay={0.2}>
                          <StreakIndicator userId={user?.id} token={token} />
                        </CardTransition>
                        
                        {/* Learning DNA */}
                        <CardTransition delay={0.3}>
                          <LearningDNA userId={user?.id} token={token} />
                        </CardTransition>
                        
                        {/* Learning Style */}
                        <CardTransition delay={0.4}>
                          <LearningStyleCard userId={user?.id} token={token} />
                        </CardTransition>
                      </div>
                    </StaggerContainer>
                  )}

                  {activeTab === 'quests' && (
                    <StaggerContainer>
                      <div className="space-y-8">
                        {/* Quest Board */}
                        <CardTransition delay={0.1}>
                          <QuestBoard userId={user?.id} token={token} />
                        </CardTransition>
                      </div>
                    </StaggerContainer>
                  )}

                  {activeTab === 'story' && (
                    <StaggerContainer>
                      <div className="space-y-8">
                        {/* Story Dashboard */}
                        <CardTransition delay={0.1}>
                          <StoryDashboard userId={user?.id} token={token} />
                        </CardTransition>
                      </div>
                    </StaggerContainer>
                  )}

                  {activeTab === 'insights' && (
                    <StaggerContainer>
                      <div className="space-y-8">
                        {/* Learning Insights */}
                        <CardTransition delay={0.1}>
                          <LearningInsights userId={user?.id} token={token} />
                        </CardTransition>
                        
                        {/* Custom Exercises */}
                        <CardTransition delay={0.2}>
                          <CustomExercises userId={user?.id} token={token} />
                        </CardTransition>
                        
                        {/* Knowledge Graph */}
                        <CardTransition delay={0.3}>
                          {user?.id && (<KnowledgeGraph userId={user.id} />)}
                        </CardTransition>
                      </div>
                    </StaggerContainer>
                  )}

                  {activeTab === 'coding' && (
                    <StaggerContainer>
                      <div className="space-y-8">
                        <CardTransition delay={0.1}>
                          <CodingSandbox />
                        </CardTransition>
                      </div>
                    </StaggerContainer>
                  )}

                  {activeTab === 'lab' && (
                    <StaggerContainer>
                      <div className="space-y-8">
                        <CardTransition delay={0.1}>
                          <VisualizationLab />
                        </CardTransition>
                      </div>
                    </StaggerContainer>
                  )}

                  {activeTab === 'curriculum' && (
                    <StaggerContainer>
                      <div className="space-y-8">
                        {/* Adaptive Learning Path */}
                        <CardTransition delay={0.1}>
                          <AdaptivePath userId={user?.id} token={token} />
                        </CardTransition>
                        
                        {/* Fresh Lessons */}
                        <CardTransition delay={0.2}>
                          <FreshLessons userId={user?.id} token={token} />
                        </CardTransition>
                      </div>
                    </StaggerContainer>
                  )}

                  {activeTab === 'updates' && (
                    <StaggerContainer>
                      <div className="space-y-8">
                        {/* Curriculum Updates */}
                        <CardTransition delay={0.1}>
                          <CurriculumUpdates userId={user?.id} token={token} />
                        </CardTransition>
                      </div>
                    </StaggerContainer>
                  )}

                  {/* {activeTab === 'debate' && (
                    <StaggerContainer>
                      <div className="space-y-8">
                        <div className="flex items-center justify-between">
                          <div>
                            <h2 className="text-2xl font-bold text-gray-800 dark:text-white">AI Socratic Debate</h2>
                            <p className="text-gray-600 dark:text-gray-300">Challenge your critical thinking with AI-powered debates</p>
                          </div>
                          <motion.button
                            whileHover={{ scale: 1.05 }}
                            whileTap={{ scale: 0.95 }}
                            onClick={() => setShowDebatePanel(true)}
                            className="px-6 py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 flex items-center gap-2"
                          >
                            <MessageCircle className="w-5 h-5" />
                            Start New Debate
                          </motion.button>
                        </div>
                        <CardTransition delay={0.1}>
                          <DebateHistory />
                        </CardTransition>
                      </div>
                    </StaggerContainer>
                  )} */}
                  </div>
                </div>
              </CardTransition>

              {/* Feedback Card */}
              {currentFeedback && (
                <FeedbackCard
                  feedback={currentFeedback}
                  onClose={clearCurrentFeedback}
                  autoClose={true}
                />
              )}

              {/* Review Flow Modal */}
              <ModalTransition 
                isOpen={showReviewFlow} 
                onClose={() => setShowReviewFlow(false)}
                className="bg-white dark:bg-gray-800 rounded-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto shadow-2xl"
              >
                <div className="p-6 border-b border-gray-200 dark:border-gray-700 flex justify-between items-center">
                  <h2 className="text-xl font-semibold text-gray-800 dark:text-white">Review Session</h2>
                  <motion.button
                    whileHover={{ scale: 1.1 }}
                    whileTap={{ scale: 0.9 }}
                    onClick={() => setShowReviewFlow(false)}
                    className="text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                  >
                    ✕
                  </motion.button>
                </div>
                <div className="p-6">
                  <ReviewFlow
                    userId={user?.id}
                    token={token}
                    onComplete={handleReviewComplete}
                  />
                </div>
              </ModalTransition>

              {/* Badge Modal */}
              <BadgeModal
                isOpen={showBadgeModal}
                onClose={() => setShowBadgeModal(false)}
                userId={user?.id}
                token={token}
              />

              {/* Development Settings - Temporarily disabled */}
              {/* <DevSettings
                onToggleEmotionDetector={setShowEmotionDetector}
                showEmotionDetector={showEmotionDetector}
              /> */}

              {/* Story Rewards Popup */}
              <RewardsPopup
                rewards={rewards}
                isOpen={showRewards}
                onClose={closeRewards}
              />

              {/* Co-Learner */}
              <CoLearnerWidget onOpen={() => setShowCoPanel(true)} />
              <CoLearnerPanel isOpen={showCoPanel} onClose={() => setShowCoPanel(false)} />
              
              {/* Debate Panel - Hidden for now */}
              {/* <DebatePanel isOpen={showDebatePanel} onClose={() => setShowDebatePanel(false)} /> */}
            </div>
          ) : (
            <div className="flex items-center justify-center min-h-screen">
              <div className="text-center">
                <div className="w-16 h-16 bg-gradient-to-r from-blue-600 to-purple-600 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Brain className="w-8 h-8 text-white" />
                </div>
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">Welcome to AI Tutor</h2>
                <p className="text-gray-600 dark:text-gray-300">Please log in to continue your learning journey</p>
              </div>
            </div>
          )}
        </div>
      </PageTransition>
    </div>
  )
}

