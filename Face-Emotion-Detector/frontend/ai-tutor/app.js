/**
 * AI Tutor Frontend Application
 * Emotion-Adaptive Learning System
 */

class AITutorApp {
    constructor() {
        this.detector = null;
        this.isDetecting = false;
        this.currentEmotion = null;
        this.emotions = {};
        this.sessionStartTime = null;
        this.sessionTimer = null;
        this.adaptationHistory = [];
        this.learningProgress = 0;
        this.currentDifficulty = 0.3;
        
        this.emotionColors = {
            happy: { color: '#10b981', icon: '😊', bg: 'linear-gradient(135deg, #10b981, #34d399)' },
            sad: { color: '#3b82f6', icon: '😢', bg: 'linear-gradient(135deg, #3b82f6, #60a5fa)' },
            angry: { color: '#ef4444', icon: '😠', bg: 'linear-gradient(135deg, #ef4444, #f87171)' },
            fear: { color: '#8b5cf6', icon: '😨', bg: 'linear-gradient(135deg, #8b5cf6, #a78bfa)' },
            surprise: { color: '#f59e0b', icon: '😲', bg: 'linear-gradient(135deg, #f59e0b, #fbbf24)' },
            disgust: { color: '#84cc16', icon: '🤢', bg: 'linear-gradient(135deg, #84cc16, #a3e635)' },
            neutral: { color: '#6b7280', icon: '😐', bg: 'linear-gradient(135deg, #6b7280, #9ca3af)' }
        };

        this.learningContent = {
            beginner: [
                {
                    title: "Introduction to Variables",
                    content: "Variables are containers for storing data values. In programming, we use variables to hold information that can be used later in our code.",
                    difficulty: 0.2
                },
                {
                    title: "Understanding Functions",
                    content: "Functions are reusable blocks of code that perform specific tasks. They help us organize our code and avoid repetition.",
                    difficulty: 0.3
                }
            ],
            intermediate: [
                {
                    title: "Object-Oriented Programming",
                    content: "OOP is a programming paradigm based on the concept of 'objects', which contain data and code. It helps create more organized and maintainable code.",
                    difficulty: 0.6
                },
                {
                    title: "Data Structures and Algorithms",
                    content: "Data structures are ways of organizing data, while algorithms are step-by-step procedures for solving problems efficiently.",
                    difficulty: 0.7
                }
            ],
            advanced: [
                {
                    title: "Machine Learning Fundamentals",
                    content: "Machine learning is a subset of artificial intelligence that enables computers to learn and make decisions from data without being explicitly programmed.",
                    difficulty: 0.9
                },
                {
                    title: "Advanced System Design",
                    content: "System design involves creating scalable, reliable, and efficient systems that can handle large amounts of data and users.",
                    difficulty: 1.0
                }
            ]
        };

        this.init();
    }

    init() {
        this.bindEvents();
        this.initializeDetector();
        this.startSessionTimer();
        this.loadWelcomeContent();
    }

    bindEvents() {
        // Detection controls
        document.getElementById('startDetection').addEventListener('click', () => this.startDetection());
        document.getElementById('stopDetection').addEventListener('click', () => this.stopDetection());
        
        // Learning controls
        document.getElementById('startLearning').addEventListener('click', () => this.startLearning());
        document.getElementById('nextLesson').addEventListener('click', () => this.nextLesson());
        document.getElementById('prevLesson').addEventListener('click', () => this.prevLesson());
        
        // Modal controls
        document.getElementById('closeModal').addEventListener('click', () => this.closeModal());
        
        // Close modal on outside click
        document.getElementById('progressModal').addEventListener('click', (e) => {
            if (e.target.id === 'progressModal') {
                this.closeModal();
            }
        });
    }

    initializeDetector() {
        this.detector = new EmotionDetectorIntegration({
            apiUrl: 'http://localhost:5000',
            detectionInterval: 2000, // Analyze every 2 seconds
            onEmotionDetected: (data) => this.handleEmotionDetected(data),
            onError: (error) => this.handleDetectionError(error)
        });
    }

    async startDetection() {
        const video = document.getElementById('emotionVideo');
        const success = await this.detector.startCamera(video);
        
        if (success) {
            this.isDetecting = true;
            this.updateDetectionUI(true);
            this.updateEmotionStatus('Analyzing emotions...', 'success');
        } else {
            this.updateEmotionStatus('Camera access denied', 'error');
        }
    }

    stopDetection() {
        this.detector.stopCamera();
        this.isDetecting = false;
        this.updateDetectionUI(false);
        this.updateEmotionStatus('Detection paused', 'warning');
        this.hideEmotionOverlay();
    }

    handleEmotionDetected(data) {
        this.currentEmotion = data.dominant_emotion;
        this.emotions = data.emotions;
        
        this.updateEmotionDisplay();
        this.adaptLearningExperience();
        this.updateInsights();
        this.logAdaptation();
    }

    handleDetectionError(error) {
        console.error('Detection error:', error);
        this.updateEmotionStatus('Detection error', 'error');
    }

    updateDetectionUI(isActive) {
        const startBtn = document.getElementById('startDetection');
        const stopBtn = document.getElementById('stopDetection');
        
        startBtn.disabled = isActive;
        stopBtn.disabled = !isActive;
        
        if (isActive) {
            startBtn.innerHTML = '<i class="fas fa-play"></i> Analyzing...';
        } else {
            startBtn.innerHTML = '<i class="fas fa-play"></i> Start Analysis';
        }
    }

    updateEmotionStatus(message, type) {
        const statusElement = document.getElementById('emotionStatus');
        const statusDot = statusElement.querySelector('.status-dot');
        
        statusElement.querySelector('span:last-child').textContent = message;
        
        // Update status dot color
        statusDot.className = 'status-dot';
        if (type === 'success') statusDot.style.background = '#10b981';
        else if (type === 'error') statusDot.style.background = '#ef4444';
        else if (type === 'warning') statusDot.style.background = '#f59e0b';
    }

    updateEmotionDisplay() {
        if (!this.currentEmotion) return;

        const emotionData = this.emotionColors[this.currentEmotion];
        const overlay = document.getElementById('emotionOverlay');
        const text = document.getElementById('emotionText');
        const confidence = document.getElementById('emotionConfidence');

        // Update overlay (green label style)
        overlay.style.display = 'block';
        overlay.style.background = emotionData.bg ? emotionData.bg : '#16a34a';
        overlay.style.borderColor = emotionData.color || '#22c55e';
        text.textContent = this.currentEmotion.charAt(0).toUpperCase() + this.currentEmotion.slice(1);
        confidence.textContent = `${this.emotions[this.currentEmotion].toFixed(1)}%`;

        // Update emotion bars
        this.updateEmotionBars();
        
        // Show emotion details
        document.getElementById('emotionDetails').classList.add('show');
    }

    updateEmotionBars() {
        const barsContainer = document.getElementById('emotionBars');
        barsContainer.innerHTML = '';

        Object.entries(this.emotions).forEach(([emotion, confidence]) => {
            const barDiv = document.createElement('div');
            barDiv.className = `emotion-bar emotion-${emotion}`;
            
            const emotionData = this.emotionColors[emotion];
            
            barDiv.innerHTML = `
                <div class="emotion-bar-label">${emotion.charAt(0).toUpperCase() + emotion.slice(1)}</div>
                <div class="emotion-bar-container">
                    <div class="emotion-bar-fill" style="width: ${confidence}%; background: ${emotionData.bg}"></div>
                </div>
                <div class="emotion-bar-value">${confidence.toFixed(1)}%</div>
            `;
            
            barsContainer.appendChild(barDiv);
        });
    }

    hideEmotionOverlay() {
        document.getElementById('emotionOverlay').style.display = 'none';
        document.getElementById('emotionDetails').classList.remove('show');
    }

    adaptLearningExperience() {
        if (!this.currentEmotion) return;

        const adaptations = {
            happy: { difficulty: 0.1, speed: 1.2, message: "Great! You're feeling confident. Let's try something more challenging!" },
            sad: { difficulty: -0.1, speed: 0.8, message: "I notice you might be struggling. Let's slow down and review the basics." },
            angry: { difficulty: -0.15, speed: 0.7, message: "Take a deep breath. Let's try a different approach to this topic." },
            fear: { difficulty: -0.2, speed: 0.6, message: "It's okay to feel uncertain. Let's break this down into smaller steps." },
            surprise: { difficulty: 0.05, speed: 1.1, message: "Interesting! You seem surprised. Let's explore this concept further." },
            disgust: { difficulty: -0.1, speed: 0.9, message: "I see this topic isn't resonating. Let's try a different angle." },
            neutral: { difficulty: 0, speed: 1.0, message: "You seem focused. Let's continue at this pace." }
        };

        const adaptation = adaptations[this.currentEmotion];
        this.currentDifficulty = Math.max(0, Math.min(1, this.currentDifficulty + adaptation.difficulty));
        
        this.updateDifficultyIndicator();
        this.updateLearningContent();
        this.updateInsightMessage(adaptation.message);
    }

    updateDifficultyIndicator() {
        const levelBar = document.querySelector('.level-bar');
        levelBar.style.width = `${this.currentDifficulty * 100}%`;
    }

    updateLearningContent() {
        let contentLevel = 'beginner';
        if (this.currentDifficulty > 0.7) contentLevel = 'advanced';
        else if (this.currentDifficulty > 0.4) contentLevel = 'intermediate';

        const content = this.learningContent[contentLevel][0]; // Simplified for demo
        document.getElementById('lessonTitle').textContent = content.title;
        document.getElementById('lessonContent').innerHTML = `
            <div class="lesson-text">
                <h3>${content.title}</h3>
                <p>${content.content}</p>
                <div class="lesson-progress">
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: ${this.learningProgress}%"></div>
                    </div>
                    <span class="progress-text">${this.learningProgress}% Complete</span>
                </div>
            </div>
        `;
    }

    updateInsightMessage(message) {
        const insightCard = document.getElementById('currentInsight');
        insightCard.querySelector('.insight-text p').textContent = message;
        insightCard.classList.add('fade-in');
        
        setTimeout(() => {
            insightCard.classList.remove('fade-in');
        }, 500);
    }

    updateInsights() {
        // Update insights based on current emotion and progress
        const insights = {
            happy: "Your positive attitude is helping you learn faster!",
            sad: "Don't worry, learning takes time. We'll find the right pace for you.",
            angry: "Let's try a different approach. Sometimes a fresh perspective helps.",
            fear: "It's normal to feel uncertain. We'll build your confidence step by step.",
            surprise: "Your curiosity is a great learning asset!",
            disgust: "Let's find a topic that interests you more.",
            neutral: "You're maintaining good focus. Keep it up!"
        };

        this.updateInsightMessage(insights[this.currentEmotion] || insights.neutral);
    }

    logAdaptation() {
        const logEntry = {
            time: new Date().toLocaleTimeString(),
            action: `Adapted difficulty to ${(this.currentDifficulty * 100).toFixed(0)}% based on ${this.currentEmotion} emotion`,
            emotion: this.currentEmotion
        };

        this.adaptationHistory.unshift(logEntry);
        if (this.adaptationHistory.length > 5) {
            this.adaptationHistory = this.adaptationHistory.slice(0, 5);
        }

        this.updateAdaptationLog();
    }

    updateAdaptationLog() {
        const logEntries = document.getElementById('logEntries');
        logEntries.innerHTML = '';

        this.adaptationHistory.forEach(entry => {
            const logDiv = document.createElement('div');
            logDiv.className = 'log-entry fade-in';
            logDiv.innerHTML = `
                <span class="log-time">${entry.time}</span>
                <span class="log-action">${entry.action}</span>
            `;
            logEntries.appendChild(logDiv);
        });
    }

    startLearning() {
        document.querySelector('.welcome-message').style.display = 'none';
        this.updateLearningContent();
        this.learningProgress = 10;
        this.updateProgress();
    }

    nextLesson() {
        this.learningProgress = Math.min(100, this.learningProgress + 20);
        this.updateProgress();
        this.updateLearningContent();
    }

    prevLesson() {
        this.learningProgress = Math.max(0, this.learningProgress - 20);
        this.updateProgress();
        this.updateLearningContent();
    }

    updateProgress() {
        document.getElementById('progress').textContent = `${this.learningProgress}%`;
    }

    loadWelcomeContent() {
        // Initial welcome content is already in HTML
    }

    startSessionTimer() {
        this.sessionStartTime = Date.now();
        this.sessionTimer = setInterval(() => {
            const elapsed = Date.now() - this.sessionStartTime;
            const minutes = Math.floor(elapsed / 60000);
            const seconds = Math.floor((elapsed % 60000) / 1000);
            document.getElementById('sessionTime').textContent = 
                `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
        }, 1000);
    }

    closeModal() {
        document.getElementById('progressModal').classList.remove('show');
    }

    showProgressModal() {
        document.getElementById('progressModal').classList.add('show');
    }

    // Public methods for external access
    getCurrentEmotion() {
        return this.currentEmotion;
    }

    getLearningProgress() {
        return this.learningProgress;
    }

    getAdaptationHistory() {
        return this.adaptationHistory;
    }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.aiTutorApp = new AITutorApp();
    
    // Add some demo functionality
    console.log('AI Tutor App initialized!');
    console.log('Available methods:');
    console.log('- aiTutorApp.getCurrentEmotion()');
    console.log('- aiTutorApp.getLearningProgress()');
    console.log('- aiTutorApp.getAdaptationHistory()');
});

// Handle page visibility changes
document.addEventListener('visibilitychange', () => {
    if (document.hidden && window.aiTutorApp?.isDetecting) {
        console.log('Page hidden - pausing detection');
    } else if (!document.hidden && window.aiTutorApp?.isDetecting) {
        console.log('Page visible - resuming detection');
    }
});

// Handle page unload
window.addEventListener('beforeunload', () => {
    if (window.aiTutorApp?.detector) {
        window.aiTutorApp.detector.destroy();
    }
});
