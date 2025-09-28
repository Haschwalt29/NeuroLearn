import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Settings, Eye, Code, Bug } from 'lucide-react';

const DevSettings = ({ onToggleEmotionDetector, showEmotionDetector }) => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="fixed bottom-4 right-4 z-50">
      <motion.div
        initial={{ scale: 0 }}
        animate={{ scale: 1 }}
        transition={{ delay: 1, type: "spring", stiffness: 200 }}
        className="bg-white rounded-lg shadow-lg border border-gray-200"
      >
        {/* Toggle Button */}
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="p-3 hover:bg-gray-50 rounded-lg transition-colors"
          title="Development Settings"
        >
          <Settings className="w-5 h-5 text-gray-600" />
        </button>

        {/* Settings Panel */}
        <AnimatePresence>
          {isOpen && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="absolute bottom-full right-0 mb-2 w-64 bg-white rounded-lg shadow-lg border border-gray-200 p-4"
            >
              <div className="space-y-4">
                <div className="flex items-center gap-2 text-sm font-medium text-gray-700">
                  <Code className="w-4 h-4" />
                  Development Tools
                </div>
                
                <div className="space-y-3">
                  <label className="flex items-center justify-between cursor-pointer">
                    <div className="flex items-center gap-2">
                      <Eye className="w-4 h-4 text-blue-600" />
                      <span className="text-sm text-gray-700">Live Emotion Detector</span>
                    </div>
                    <button
                      onClick={() => onToggleEmotionDetector(!showEmotionDetector)}
                      className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                        showEmotionDetector ? 'bg-blue-600' : 'bg-gray-200'
                      }`}
                    >
                      <span
                        className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                          showEmotionDetector ? 'translate-x-6' : 'translate-x-1'
                        }`}
                      />
                    </button>
                  </label>
                  
                  <div className="text-xs text-gray-500">
                    {showEmotionDetector 
                      ? 'Live emotion detection interface is visible' 
                      : 'Live emotion detection interface is hidden'
                    }
                  </div>
                </div>

                <div className="pt-2 border-t border-gray-100">
                  <div className="flex items-center gap-2 text-xs text-gray-500">
                    <Bug className="w-3 h-3" />
                    Development Mode Active
                  </div>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>
    </div>
  );
};

export default DevSettings;
