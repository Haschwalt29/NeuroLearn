import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Trophy, 
  Star, 
  Gift, 
  Sparkles, 
  X,
  CheckCircle,
  Zap,
  Crown,
  Gem
} from 'lucide-react';

const RewardsPopup = ({ rewards, isOpen, onClose, onRewardViewed }) => {
  const [currentRewardIndex, setCurrentRewardIndex] = useState(0);
  const [showReward, setShowReward] = useState(false);

  useEffect(() => {
    if (isOpen && rewards && rewards.length > 0) {
      setCurrentRewardIndex(0);
      setShowReward(true);
    }
  }, [isOpen, rewards]);

  const handleNextReward = () => {
    if (currentRewardIndex < rewards.length - 1) {
      setCurrentRewardIndex(currentRewardIndex + 1);
    } else {
      handleClose();
    }
  };

  const handleClose = () => {
    setShowReward(false);
    setTimeout(() => {
      onClose();
    }, 300);
  };

  const getRewardIcon = (type) => {
    switch (type) {
      case 'xp':
        return <Zap className="w-8 h-8 text-yellow-500" />;
      case 'badge':
        return <Trophy className="w-8 h-8 text-purple-500" />;
      case 'chapter_complete':
        return <Crown className="w-8 h-8 text-blue-500" />;
      case 'chapter_unlock':
        return <Gem className="w-8 h-8 text-green-500" />;
      case 'story_milestone':
        return <Star className="w-8 h-8 text-pink-500" />;
      default:
        return <Gift className="w-8 h-8 text-gray-500" />;
    }
  };

  const getRewardColor = (type) => {
    switch (type) {
      case 'xp':
        return 'from-yellow-400 to-orange-500';
      case 'badge':
        return 'from-purple-400 to-pink-500';
      case 'chapter_complete':
        return 'from-blue-400 to-cyan-500';
      case 'chapter_unlock':
        return 'from-green-400 to-emerald-500';
      case 'story_milestone':
        return 'from-pink-400 to-rose-500';
      default:
        return 'from-gray-400 to-slate-500';
    }
  };

  const getRewardTitle = (reward) => {
    switch (reward.type) {
      case 'xp':
        return `+${reward.amount} XP Earned!`;
      case 'badge':
        return `New Badge: ${reward.badge_name}!`;
      case 'chapter_complete':
        return `Chapter Completed!`;
      case 'chapter_unlock':
        return `New Chapter Unlocked!`;
      case 'story_milestone':
        return `Story Milestone Reached!`;
      default:
        return 'Reward Earned!';
    }
  };

  const getRewardDescription = (reward) => {
    switch (reward.type) {
      case 'xp':
        return reward.description || `You earned ${reward.amount} experience points!`;
      case 'badge':
        return reward.description || `Congratulations! You've earned the "${reward.badge_name}" badge!`;
      case 'chapter_complete':
        return reward.description || `You've completed "${reward.chapter_title}"!`;
      case 'chapter_unlock':
        return reward.description || `"${reward.chapter_title}" is now available!`;
      case 'story_milestone':
        return reward.description || 'You\'ve reached an important milestone in your story!';
      default:
        return reward.description || 'You\'ve earned a reward!';
    }
  };

  if (!isOpen || !rewards || rewards.length === 0) {
    return null;
  }

  const currentReward = rewards[currentRewardIndex];

  return (
    <AnimatePresence>
      {showReward && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
        >
          <motion.div
            initial={{ scale: 0.5, opacity: 0, y: 50 }}
            animate={{ scale: 1, opacity: 1, y: 0 }}
            exit={{ scale: 0.5, opacity: 0, y: 50 }}
            transition={{ type: "spring", stiffness: 300, damping: 30 }}
            className="bg-white rounded-2xl shadow-2xl max-w-md w-full p-8 relative overflow-hidden"
          >
            {/* Background Effects */}
            <div className="absolute inset-0 bg-gradient-to-br from-purple-50 to-blue-50 opacity-50"></div>
            <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-br from-yellow-200 to-orange-200 rounded-full -translate-y-16 translate-x-16 opacity-20"></div>
            <div className="absolute bottom-0 left-0 w-24 h-24 bg-gradient-to-tr from-green-200 to-blue-200 rounded-full translate-y-12 -translate-x-12 opacity-20"></div>

            {/* Close Button */}
            <button
              onClick={handleClose}
              className="absolute top-4 right-4 text-gray-400 hover:text-gray-600 transition-colors z-10"
            >
              <X className="w-6 h-6" />
            </button>

            {/* Reward Content */}
            <div className="relative z-10 text-center">
              {/* Icon with Animation */}
              <motion.div
                initial={{ scale: 0, rotate: -180 }}
                animate={{ scale: 1, rotate: 0 }}
                transition={{ delay: 0.2, type: "spring", stiffness: 200 }}
                className="mb-6"
              >
                <div className={`w-20 h-20 mx-auto bg-gradient-to-r ${getRewardColor(currentReward.type)} rounded-full flex items-center justify-center shadow-lg`}>
                  {getRewardIcon(currentReward.type)}
                </div>
              </motion.div>

              {/* Sparkle Effects */}
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.5 }}
                className="absolute inset-0 pointer-events-none"
              >
                {[...Array(6)].map((_, i) => (
                  <motion.div
                    key={i}
                    initial={{ opacity: 0, scale: 0 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: 0.7 + i * 0.1 }}
                    className="absolute"
                    style={{
                      top: `${20 + (i * 15)}%`,
                      left: `${15 + (i * 12)}%`,
                    }}
                  >
                    <Sparkles className="w-4 h-4 text-yellow-400" />
                  </motion.div>
                ))}
              </motion.div>

              {/* Title */}
              <motion.h2
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 }}
                className="text-2xl font-bold text-gray-900 mb-4"
              >
                {getRewardTitle(currentReward)}
              </motion.h2>

              {/* Description */}
              <motion.p
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.4 }}
                className="text-gray-600 mb-6 leading-relaxed"
              >
                {getRewardDescription(currentReward)}
              </motion.p>

              {/* Progress Indicator */}
              {rewards.length > 1 && (
                <div className="flex justify-center mb-6">
                  <div className="flex space-x-2">
                    {rewards.map((_, index) => (
                      <div
                        key={index}
                        className={`w-2 h-2 rounded-full transition-colors ${
                          index === currentRewardIndex ? 'bg-purple-600' : 'bg-gray-300'
                        }`}
                      />
                    ))}
                  </div>
                </div>
              )}

              {/* Action Buttons */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.5 }}
                className="flex gap-3 justify-center"
              >
                {rewards.length > 1 && currentRewardIndex < rewards.length - 1 ? (
                  <button
                    onClick={handleNextReward}
                    className="px-6 py-3 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-lg font-medium hover:from-purple-700 hover:to-blue-700 transition-all duration-200 shadow-lg"
                  >
                    Next Reward
                  </button>
                ) : (
                  <button
                    onClick={handleClose}
                    className="px-6 py-3 bg-gradient-to-r from-green-600 to-emerald-600 text-white rounded-lg font-medium hover:from-green-700 hover:to-emerald-700 transition-all duration-200 shadow-lg flex items-center gap-2"
                  >
                    <CheckCircle className="w-5 h-5" />
                    Awesome!
                  </button>
                )}
              </motion.div>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
};

export default RewardsPopup;
