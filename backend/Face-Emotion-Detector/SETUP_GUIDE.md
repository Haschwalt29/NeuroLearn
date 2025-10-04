# 🚀 AI Tutor Setup Guide

Complete setup instructions for the AI Tutor - Emotion-Adaptive Learning System.

## 📋 Prerequisites

- **Python 3.7+** with pip
- **Modern web browser** (Chrome, Firefox, Safari, Edge)
- **Webcam** for emotion detection
- **Internet connection** for initial model downloads

## 🛠️ Installation

### 1. Clone/Download the Project
```bash
# If you have git
git clone <your-repo-url>
cd Face-Emotion-Detector

# Or download and extract the ZIP file
```

### 2. Install Python Dependencies
```bash
# Install all required packages
pip install -r requirements.txt

# Or install individually
pip install tensorflow keras pandas numpy opencv-contrib-python deepface matplotlib flask tf-keras
```

### 3. Verify Installation
```bash
# Test the backend
python simple_pretrained_demo.py

# Should show emotion detection results
```

## 🚀 Quick Start

### Option 1: Automated Startup (Recommended)
```bash
# Start both backend and frontend
python start-ai-tutor.py
```

This will:
- ✅ Check all dependencies
- 🚀 Start the Flask backend (port 5000)
- 🎨 Start the frontend server (port 8080)
- 🌐 Open your browser automatically

### Option 2: Manual Startup

#### Start Backend
```bash
# Terminal 1 - Backend
python web_app.py
```

#### Start Frontend
```bash
# Terminal 2 - Frontend
cd ai-tutor-frontend
python -m http.server 8080
```

#### Access the Application
- **Main App**: http://localhost:8080
- **Demo Page**: http://localhost:8080/demo.html
- **Backend API**: http://localhost:5000

## 🎯 First Time Setup

### 1. Allow Camera Access
When you first open the app, your browser will ask for camera permission:
- Click **"Allow"** to enable emotion detection
- The app needs camera access to analyze your emotions

### 2. Test Emotion Detection
1. Click **"Start Analysis"** in the emotion panel
2. Look at the camera and make different facial expressions
3. Watch the AI detect and display your emotions in real-time

### 3. Experience Adaptive Learning
1. Click **"Begin Learning Journey"** to start
2. The AI will adapt the content based on your emotions
3. Try different expressions to see how it responds

## 🔧 Configuration

### Backend Configuration
Edit `web_app.py` to modify:
- **API endpoints**
- **CORS settings**
- **Model parameters**

### Frontend Configuration
Edit `ai-tutor-frontend/app.js` to customize:
- **Learning content**
- **Emotion adaptations**
- **UI behavior**

### Emotion Detection Settings
Edit `ai-tutor-frontend/emotion-integration.js` to adjust:
- **Detection interval** (default: 2 seconds)
- **API endpoints**
- **Error handling**

## 📱 Browser Compatibility

### Supported Browsers
- ✅ **Chrome 80+** (Recommended)
- ✅ **Firefox 75+**
- ✅ **Safari 13+**
- ✅ **Edge 80+**

### Required Features
- **Camera API** support
- **WebRTC** for video capture
- **ES6+** JavaScript support

## 🐛 Troubleshooting

### Common Issues

#### 1. Camera Not Working
```bash
# Check browser permissions
# Make sure no other app is using the camera
# Try refreshing the page
```

#### 2. Backend Connection Error
```bash
# Check if Flask is running
curl http://localhost:5000

# Check for port conflicts
netstat -an | grep 5000
```

#### 3. Model Download Issues
```bash
# DeepFace downloads models on first run
# This may take a few minutes
# Check internet connection
```

#### 4. Dependencies Missing
```bash
# Reinstall requirements
pip install --upgrade -r requirements.txt

# For tf-keras specifically
pip install tf-keras
```

### Performance Issues

#### Slow Emotion Detection
- Increase `detectionInterval` in `emotion-integration.js`
- Close other camera-using applications
- Check system resources

#### High CPU Usage
- Reduce video resolution in camera settings
- Increase detection interval
- Close unnecessary browser tabs

## 🔒 Security & Privacy

### Data Handling
- ✅ **No personal data stored**
- ✅ **Local processing only**
- ✅ **No video recording**
- ✅ **Temporary analysis only**

### Network Security
- 🔒 **HTTPS recommended** for production
- 🔒 **Local API calls** only
- 🔒 **No external data transmission**

## 🚀 Production Deployment

### Backend Deployment
```bash
# Using Gunicorn (recommended)
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 web_app:app

# Using Docker
docker build -t ai-tutor-backend .
docker run -p 5000:5000 ai-tutor-backend
```

### Frontend Deployment
```bash
# Static hosting (Netlify, Vercel, etc.)
# Upload ai-tutor-frontend/ folder
# Configure API URL for production backend
```

### Environment Variables
```bash
# Production settings
export FLASK_ENV=production
export API_URL=https://your-backend.com
export DEBUG=False
```

## 📊 Monitoring & Analytics

### Backend Monitoring
- **Flask logs** for API requests
- **Error tracking** for failed analyses
- **Performance metrics** for response times

### Frontend Analytics
- **User interactions** tracking
- **Emotion detection** success rates
- **Learning progress** metrics

## 🔄 Updates & Maintenance

### Updating Dependencies
```bash
# Update Python packages
pip install --upgrade -r requirements.txt

# Update frontend dependencies
cd ai-tutor-frontend
# No package manager needed for vanilla JS
```

### Model Updates
- DeepFace models update automatically
- Check for new model versions
- Monitor accuracy improvements

## 📞 Support

### Getting Help
1. **Check this guide** for common issues
2. **Review error messages** in browser console
3. **Check backend logs** for API errors
4. **Create an issue** in the repository

### Debug Mode
```bash
# Enable debug logging
export FLASK_DEBUG=1
python web_app.py
```

### Log Files
- **Backend logs**: Console output
- **Frontend logs**: Browser Developer Tools
- **Error logs**: Check browser console

## 🎉 Success!

If everything is working correctly, you should see:
- ✅ **Camera feed** in the emotion panel
- ✅ **Real-time emotion detection** with confidence scores
- ✅ **Adaptive learning content** that changes based on emotions
- ✅ **AI insights** and recommendations
- ✅ **Progress tracking** and analytics

## 🚀 Next Steps

1. **Customize learning content** for your specific use case
2. **Adjust emotion adaptations** based on your needs
3. **Add new features** like user accounts or progress saving
4. **Deploy to production** for real users
5. **Monitor and optimize** performance

---

**Happy Learning! 🎓✨**
