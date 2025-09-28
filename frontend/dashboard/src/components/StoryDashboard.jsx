import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  BookOpen, 
  Lock, 
  Unlock, 
  CheckCircle, 
  Star, 
  Trophy,
  Play,

  Eye,
  Sparkles
} from 'lucide-react';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'https://neurolearn-6c0k.onrender.com';

const StoryDashboard = ({ userId, token }) => {
  const [storyData, setStoryData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedChapter, setSelectedChapter] = useState(null);
  const [showCutscene, setShowCutscene] = useState(false);

  useEffect(() => {
    fetchStoryData();
  }, [userId, token]);

  const fetchStoryData = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE_URL}/api/story/current`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error('Failed to fetch story data');
      }

      const result = await response.json();
      setStoryData(result.data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleChapterClick = (chapter) => {
    setSelectedChapter(chapter);
    if (chapter.storyline_text && !chapter.is_completed) {
      setShowCutscene(true);
    }
  };

  const handleQuestClick = async (quest) => {
    if (quest.is_completed) return;
    
    // In a real implementation, this would start the quest
    console.log('Starting quest:', quest.title);
    // You would navigate to the quest interface here
  };

  const getDifficultyColor = (difficulty) => {
    switch (difficulty) {
      case 'easy': return 'text-green-600 bg-green-100';
      case 'medium': return 'text-yellow-600 bg-yellow-100';
      case 'hard': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getQuestTypeIcon = (type) => {
    switch (type) {
      case 'learning': return <BookOpen className="w-4 h-4" />;
      case 'practice': return <Play className="w-4 h-4" />;
      case 'challenge': return <Trophy className="w-4 h-4" />;
      default: return <Star className="w-4 h-4" />;
    }
  };

  if (loading) {
    return (
      <div className="bg-white rounded-xl shadow-lg p-6">
        <div className="animate-pulse">
          <div className="h-6 bg-gray-200 rounded w-1/3 mb-4"></div>
          <div className="space-y-3">
            <div className="h-4 bg-gray-200 rounded"></div>
            <div className="h-4 bg-gray-200 rounded w-5/6"></div>
          </div>
        </div>
      </div>
    );
  }

  if (error || !storyData) {
    return (
      <div className="bg-white rounded-xl shadow-lg p-6">
        <div className="text-center text-red-600">
          <p>Failed to load story data: {error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl shadow-lg p-6">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 bg-gradient-to-r from-purple-600 to-blue-600 rounded-lg flex items-center justify-center">
            <BookOpen className="w-6 h-6 text-white" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-gray-900">{storyData.story.title}</h2>
            <p className="text-gray-600">{storyData.story.theme}</p>
          </div>
        </div>
        <div className="text-right">
          <div className="flex items-center gap-2 text-sm text-gray-600">
            <Sparkles className="w-4 h-4" />
            <span>{storyData.total_story_xp} XP</span>
          </div>
        </div>
      </div>

      <div className="mb-6">
        <p className="text-gray-700 leading-relaxed">{storyData.story.description}</p>
      </div>

      {/* Progress Bar */}
      <div className="mb-8">
        <div className="flex justify-between text-sm text-gray-600 mb-2">
          <span>Story Progress</span>
          <span>{storyData.completed_chapters.length} / {storyData.unlocked_chapters.length} Chapters</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-3">
          <motion.div
            className="bg-gradient-to-r from-purple-600 to-blue-600 h-3 rounded-full"
            initial={{ width: 0 }}
            animate={{ 
              width: `${(storyData.completed_chapters.length / Math.max(storyData.unlocked_chapters.length, 1)) * 100}%` 
            }}
            transition={{ duration: 1, ease: "easeOut" }}
          />
        </div>
      </div>

      {/* Chapters */}
      <div className="space-y-6">
        <h3 className="text-lg font-semibold text-gray-900">Chapters</h3>
        
        <div className="grid gap-4">
          {storyData.unlocked_chapters.map((chapter, index) => (
            <motion.div
              key={chapter.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className={`border-2 rounded-lg p-4 cursor-pointer transition-all duration-200 ${
                chapter.is_completed 
                  ? 'border-green-300 bg-green-50' 
                  : 'border-gray-200 hover:border-purple-300 hover:bg-purple-50'
              }`}
              onClick={() => handleChapterClick(chapter)}
            >
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-3">
                  {chapter.is_completed ? (
                    <CheckCircle className="w-6 h-6 text-green-600" />
                  ) : (
                    <Unlock className="w-6 h-6 text-purple-600" />
                  )}
                  <div>
                    <h4 className="font-semibold text-gray-900">{chapter.title}</h4>
                    <p className="text-sm text-gray-600">Chapter {chapter.order}</p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  {chapter.is_completed && (
                    <span className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded-full">
                      Completed
                    </span>
                  )}
                  <Eye className="w-4 h-4 text-gray-400" />
                </div>
              </div>

              <p className="text-gray-700 text-sm mb-4">{chapter.description}</p>

              {/* Quests */}
              <div className="space-y-2">
                <h5 className="text-sm font-medium text-gray-800">Quests ({chapter.quests.length})</h5>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                  {chapter.quests.map((quest) => (
                    <motion.div
                      key={quest.id}
                      whileHover={{ scale: 1.02 }}
                      className={`p-3 rounded-lg border cursor-pointer transition-all ${
                        quest.is_completed
                          ? 'border-green-200 bg-green-50'
                          : 'border-gray-200 hover:border-blue-300 hover:bg-blue-50'
                      }`}
                      onClick={(e) => {
                        e.stopPropagation();
                        handleQuestClick(quest);
                      }}
                    >
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center gap-2">
                          {getQuestTypeIcon(quest.quest_type)}
                          <span className="text-sm font-medium text-gray-900">
                            {quest.title}
                          </span>
                        </div>
                        {quest.is_completed && (
                          <CheckCircle className="w-4 h-4 text-green-600" />
                        )}
                      </div>
                      
                      <div className="flex items-center justify-between text-xs">
                        <span className={`px-2 py-1 rounded-full ${getDifficultyColor(quest.difficulty_level)}`}>
                          {quest.difficulty_level}
                        </span>
                        <span className="text-gray-600">
                          {quest.reward_xp} XP
                        </span>
                      </div>
                    </motion.div>
                  ))}
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Story Cutscene Modal */}
      <AnimatePresence>
        {showCutscene && selectedChapter && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
            onClick={() => setShowCutscene(false)}
          >
            <motion.div
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.8, opacity: 0 }}
              className="bg-white rounded-xl max-w-2xl w-full max-h-[80vh] overflow-y-auto"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-xl font-bold text-gray-900">
                    {selectedChapter.title}
                  </h3>
                  <button
                    onClick={() => setShowCutscene(false)}
                    className="text-gray-400 hover:text-gray-600"
                  >
                    ✕
                  </button>
                </div>
                
                <div className="prose max-w-none">
                  <pre className="whitespace-pre-wrap text-gray-700 leading-relaxed font-sans">
                    {selectedChapter.storyline_text}
                  </pre>
                </div>
                
                <div className="mt-6 flex justify-end">
                  <button
                    onClick={() => setShowCutscene(false)}
                    className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
                  >
                    Continue Adventure
                  </button>
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default StoryDashboard;
