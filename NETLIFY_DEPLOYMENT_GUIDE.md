# NeuroLearn Frontend - Netlify Deployment Guide

This guide will help you deploy your NeuroLearn React frontend to Netlify.

## Prerequisites

1. **Netlify Account**: Sign up at [netlify.com](https://netlify.com)
2. **GitHub Repository**: Your code should be pushed to GitHub
3. **Backend Deployed**: Your Render backend should be running

## Step-by-Step Deployment

### 1. Prepare Your Frontend

Your frontend is located in `frontend/dashboard/` and includes:
- React 18 with Vite
- Tailwind CSS for styling
- Socket.IO for real-time communication
- Multiple contexts for state management

### 2. Deploy to Netlify

#### Option A: Deploy via Netlify Dashboard

1. **Go to Netlify Dashboard**
   - Visit [app.netlify.com](https://app.netlify.com)
   - Click "Add new site" → "Import an existing project"

2. **Connect Repository**
   - Connect your GitHub account
   - Select your NeuroLearn repository
   - Click "Deploy site"

3. **Configure Build Settings**
   - **Base directory**: `frontend/dashboard`
   - **Build command**: `npm run build`
   - **Publish directory**: `dist`
   - **Node version**: `18` (recommended)

#### Option B: Deploy via Netlify CLI

```bash
# Install Netlify CLI
npm install -g netlify-cli

# Navigate to frontend directory
cd frontend/dashboard

# Deploy
netlify deploy

# Follow the prompts
```

### 3. Configure Environment Variables

In your Netlify project settings:

1. **Go to Site Settings** → **Environment Variables**
2. **Add these variables**:

**Required Variables:**
```
VITE_API_BASE_URL=https://neurolearn-7hk8.onrender.com
```

**Optional Variables:**
```
VITE_SOCKET_URL=https://neurolearn-7hk8.onrender.com
VITE_ENV=production
```

### 4. Configure Domain (Optional)

1. **Custom Domain**: Add your custom domain in Domain Settings
2. **Subdomain**: Use the provided Netlify subdomain (e.g., `neurolearn-frontend.netlify.app`)

## Configuration Files Explained

### netlify.toml
```toml
[build]
  base = "frontend/dashboard"
  command = "npm run build"
  publish = "dist"

[build.environment]
  NODE_VERSION = "18"

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
```

### Environment Variables
- `VITE_API_BASE_URL`: Points to your Render backend
- `VITE_SOCKET_URL`: Socket.IO connection URL
- `VITE_ENV`: Environment indicator

## Frontend Features

Your deployed frontend will include:

### **Core Pages**
- **Login**: User authentication
- **Dashboard**: Main learning interface
- **Settings**: User preferences and co-learner configuration
- **Feedback**: Learning feedback and insights
- **Revision**: Spaced repetition system
- **Admin**: Teacher/admin dashboard

### **Advanced Features**
- **AI Co-Learner**: Interactive study buddy with multiple personas
- **Emotion Detection**: Real-time emotion analysis
- **Learning DNA**: Personalized learning profiles
- **Gamification**: Quests, badges, and achievements
- **Real-time Updates**: Socket.IO integration
- **3D Visualizations**: Three.js powered learning visualizations

## Testing Your Deployment

### 1. **Basic Functionality**
- Visit your Netlify URL
- Test user registration/login
- Check API connectivity

### 2. **Core Features**
- Test co-learner interaction
- Verify emotion detection
- Check learning progress tracking

### 3. **Real-time Features**
- Test Socket.IO connections
- Verify live updates
- Check collaborative features

## Troubleshooting

### Common Issues

1. **Build Failures**
   - Check Node.js version compatibility
   - Verify all dependencies are installed
   - Check for TypeScript errors

2. **API Connection Issues**
   - Verify `VITE_API_BASE_URL` is correct
   - Check CORS configuration on backend
   - Test API endpoints directly

3. **Socket.IO Issues**
   - Verify Socket.IO URL configuration
   - Check WebSocket support
   - Test real-time features

4. **Environment Variables**
   - Ensure all `VITE_` prefixed variables are set
   - Check variable names match exactly
   - Verify values are correct

### Debugging

1. **Check Build Logs**: Review Netlify build logs for errors
2. **Test API Calls**: Use browser dev tools to check network requests
3. **Verify Environment**: Check if environment variables are loaded

## Performance Optimization

### **Netlify Features**
- **Automatic HTTPS**: SSL certificates included
- **Global CDN**: Fast loading worldwide
- **Edge Functions**: Serverless functions support
- **Analytics**: Built-in performance monitoring

### **Frontend Optimizations**
- **Code Splitting**: Automatic route-based splitting
- **Image Optimization**: Automatic image optimization
- **Caching**: Aggressive caching for static assets

## Monitoring

### **Netlify Analytics**
- Page views and user sessions
- Performance metrics
- Error tracking

### **Custom Monitoring**
- API response times
- User engagement metrics
- Feature usage analytics

## Security Considerations

### **Environment Variables**
- Never commit sensitive data to repository
- Use Netlify's environment variable system
- Rotate API keys regularly

### **CORS Configuration**
- Backend CORS is configured for your domain
- Verify allowed origins include your Netlify URL

## Next Steps

1. **Custom Domain**: Set up your custom domain
2. **Analytics**: Configure analytics tracking
3. **Monitoring**: Set up error monitoring (Sentry, etc.)
4. **Testing**: Implement automated testing
5. **CI/CD**: Set up continuous deployment

## Support

- **Netlify Documentation**: [docs.netlify.com](https://docs.netlify.com)
- **Netlify Community**: [community.netlify.com](https://community.netlify.com)

---

**Your NeuroLearn frontend is now ready for deployment on Netlify!** 🚀

The configuration handles all production requirements while maintaining compatibility with your existing development setup.
