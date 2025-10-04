# 🔧 AI Tutor Troubleshooting Guide

## 🚨 Common Issues and Solutions

### 1. **Detection Error (CORS Policy Error)**

**Symptoms:**
- Console shows: "Access to fetch at 'http://localhost:5000/upload' from origin 'http://localhost:8080' has been blocked by CORS policy"
- Emotion detection not working

**Solution:**
```bash
# 1. Install flask-cors
pip install flask-cors

# 2. Restart the backend
python web_app.py
```

**Verification:**
- Check browser console - CORS errors should be gone
- Backend should show "CORS enabled" in logs

### 2. **500 Internal Server Error**

**Symptoms:**
- Console shows: "POST http://localhost:5000/upload net::ERR_FAILED 500 (INTERNAL SERVER ERROR)"
- Backend logs show errors

**Solution:**
```bash
# 1. Check if all dependencies are installed
pip install -r requirements.txt

# 2. Test the backend
python test-backend.py

# 3. Check backend logs for specific errors
python web_app.py
```

**Common Causes:**
- Missing `tf-keras` package
- DeepFace model not downloaded
- Image processing errors

### 3. **Camera Not Working**

**Symptoms:**
- "Camera access denied" error
- Video feed not showing
- "Could not access camera" message

**Solution:**
1. **Check browser permissions:**
   - Click the camera icon in address bar
   - Allow camera access
   - Refresh the page

2. **Check if camera is in use:**
   - Close other apps using camera (Zoom, Teams, etc.)
   - Try different browser

3. **Test camera access:**
   ```javascript
   // Open browser console and run:
   navigator.mediaDevices.getUserMedia({video: true})
     .then(stream => console.log('Camera working'))
     .catch(err => console.log('Camera error:', err));
   ```

### 4. **No Emotion Detected**

**Symptoms:**
- Camera works but no emotions are detected
- "No emotion detected" error
- Emotion overlay not showing

**Solution:**
1. **Check lighting:**
   - Ensure good lighting on your face
   - Avoid backlighting
   - Face the camera directly

2. **Check face visibility:**
   - Make sure your face is clearly visible
   - Remove glasses if causing issues
   - Try different angles

3. **Test with sample images:**
   ```bash
   # Test with provided sample images
   python simple_pretrained_demo.py
   ```

### 5. **Slow Performance**

**Symptoms:**
- Laggy emotion detection
- High CPU usage
- Browser becomes unresponsive

**Solution:**
1. **Reduce detection frequency:**
   ```javascript
   // In emotion-integration.js, increase interval:
   detectionInterval: 3000  // Change from 2000 to 3000ms
   ```

2. **Close other applications:**
   - Close unnecessary browser tabs
   - Close other camera-using apps
   - Free up system resources

3. **Reduce video quality:**
   ```javascript
   // In startCamera method:
   video: { 
     width: { ideal: 320 },  // Reduce from 640
     height: { ideal: 240 }  // Reduce from 480
   }
   ```

### 6. **Backend Not Starting**

**Symptoms:**
- "Cannot connect to backend server"
- Port 5000 already in use
- Import errors

**Solution:**
1. **Check if port is in use:**
   ```bash
   # Windows
   netstat -an | findstr :5000
   
   # Kill process using port 5000
   taskkill /f /pid <PID>
   ```

2. **Install missing dependencies:**
   ```bash
   pip install --upgrade -r requirements.txt
   pip install tf-keras
   ```

3. **Check Python version:**
   ```bash
   python --version  # Should be 3.7+
   ```

### 7. **Frontend Not Loading**

**Symptoms:**
- "This site can't be reached"
- 404 errors
- Blank page

**Solution:**
1. **Check if frontend server is running:**
   ```bash
   cd ai-tutor-frontend
   python -m http.server 8080
   ```

2. **Check URL:**
   - Use: `http://localhost:8080`
   - Not: `https://localhost:8080`

3. **Check file permissions:**
   - Ensure all files are readable
   - Check if files exist in correct location

## 🔍 Debug Steps

### Step 1: Check Backend
```bash
# Test backend API
python test-backend.py

# Check backend logs
python web_app.py
```

### Step 2: Check Frontend
1. Open browser console (F12)
2. Look for error messages
3. Check Network tab for failed requests

### Step 3: Check Camera
```javascript
// In browser console:
navigator.mediaDevices.getUserMedia({video: true})
  .then(stream => {
    console.log('Camera working');
    stream.getTracks().forEach(track => track.stop());
  })
  .catch(err => console.log('Camera error:', err));
```

### Step 4: Check Emotion Detection
```bash
# Test with sample images
python simple_pretrained_demo.py
```

## 📊 Performance Optimization

### For Better Performance:
1. **Use Chrome browser** (best performance)
2. **Close unnecessary tabs**
3. **Ensure good lighting**
4. **Use wired internet** (if applicable)
5. **Close other camera apps**

### For Development:
1. **Enable debug logs** in browser console
2. **Check backend logs** for errors
3. **Use smaller images** for testing
4. **Increase detection interval** during development

## 🆘 Still Having Issues?

### Check System Requirements:
- **Python 3.7+** installed
- **Modern browser** (Chrome 80+, Firefox 75+, Safari 13+)
- **Webcam** working in other apps
- **Internet connection** for model downloads

### Common Error Messages:

| Error | Cause | Solution |
|-------|-------|----------|
| `CORS policy` | Backend CORS not enabled | Install flask-cors, restart backend |
| `500 Internal Server Error` | Backend processing error | Check dependencies, check logs |
| `Camera access denied` | Browser permission issue | Allow camera access, refresh page |
| `No emotion detected` | Face not visible/lighting | Improve lighting, face camera directly |
| `Failed to fetch` | Network/backend issue | Check if backend is running |

### Get Help:
1. **Check this guide** first
2. **Run the test script**: `python test-backend.py`
3. **Check browser console** for specific errors
4. **Check backend logs** for server errors
5. **Try the simple demo**: `python simple_pretrained_demo.py`

---

**Most issues are resolved by:**
1. ✅ Installing missing dependencies
2. ✅ Restarting the backend
3. ✅ Allowing camera access
4. ✅ Checking browser console for errors
