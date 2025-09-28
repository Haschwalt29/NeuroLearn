# NeuroLearn Frontend - Vercel Deployment Guide

This guide will help you deploy your NeuroLearn React frontend to Vercel.

## Prerequisites

1. **Vercel Account**: Sign up at [vercel.com](https://vercel.com)
2. **GitHub Repository**: Your code should be pushed to GitHub
3. **Backend Deployed**: Your Render backend should be running

## Step-by-Step Deployment

### 1. Prepare Your Frontend

Your frontend is located in `frontend/dashboard/` and includes:
- React 18 with Vite
- Tailwind CSS for styling
- Socket.IO for real-time communication
- Multiple contexts for state management

### 2. Deploy to Vercel

#### Option A: Deploy via Vercel Dashboard

1. **Go to Vercel Dashboard**
   - Visit [vercel.com/dashboard](https://vercel.com/dashboard)
   - Click "New Project"

2. **Import Repository**
   - Connect your GitHub account
   - Select your NeuroLearn repository
   - Choose the `frontend/dashboard` folder as the root directory

3. **Configure Build Settings**
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend/dashboard`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
   - **Install Command**: `npm install`

#### Option B: Deploy via Vercel CLI

```bash
# Install Vercel CLI
npm i -g vercel

# Navigate to frontend directory
cd frontend/dashboard

# Deploy
vercel

# Follow the prompts
```

### 3. Configure Environment Variables

In your Vercel project settings, add these environment variables:

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

1. **Custom Domain**: Add your custom domain in Vercel settings
2. **Subdomain**: Use the provided Vercel subdomain (e.g., `neurolearn-frontend.vercel.app`)

## Configuration Files Explained

### vercel.json
```json
{
  "version": 2,
  "builds": [
    {
      "src": "package.json",
      "use": "@vercel/static-build",
      "config": {
        "distDir": "dist"
      }
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "/index.html"
    }
  ]
}
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
- Visit your Vercel URL
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

1. **Check Build Logs**: Review Vercel build logs for errors
2. **Test API Calls**: Use browser dev tools to check network requests
3. **Verify Environment**: Check if environment variables are loaded

## Performance Optimization

### **Vercel Features**
- **Automatic HTTPS**: SSL certificates included
- **Global CDN**: Fast loading worldwide
- **Edge Functions**: Serverless functions support
- **Analytics**: Built-in performance monitoring

### **Frontend Optimizations**
- **Code Splitting**: Automatic route-based splitting
- **Image Optimization**: Automatic image optimization
- **Caching**: Aggressive caching for static assets

## Monitoring

### **Vercel Analytics**
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
- Use Vercel's environment variable system
- Rotate API keys regularly

### **CORS Configuration**
- Backend CORS is configured for your domain
- Verify allowed origins include your Vercel URL

## Next Steps

1. **Custom Domain**: Set up your custom domain
2. **Analytics**: Configure analytics tracking
3. **Monitoring**: Set up error monitoring (Sentry, etc.)
4. **Testing**: Implement automated testing
5. **CI/CD**: Set up continuous deployment

## Support

- **Vercel Documentation**: [vercel.com/docs](https://vercel.com/docs)
- **Vercel Community**: [github.com/vercel/vercel/discussions](https://github.com/vercel/vercel/discussions)

---

**Your NeuroLearn frontend is now ready for deployment on Vercel!** 🚀

The configuration handles all production requirements while maintaining compatibility with your existing development setup.
