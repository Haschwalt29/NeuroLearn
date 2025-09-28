# NeuroLearn Render Deployment Guide

This guide will help you deploy your NeuroLearn AI Tutor backend to Render.

## Prerequisites

1. **Render Account**: Sign up at [render.com](https://render.com)
2. **GitHub Repository**: Push your code to GitHub
3. **Database**: PostgreSQL database (Render provides this)

## Step-by-Step Deployment

### 1. Prepare Your Repository

Make sure your repository contains these files:
- `render.yaml` - Render configuration
- `Procfile` - Process definition
- `requirements.txt` - Python dependencies
- `aitutor_backend/` - Your Flask application

### 2. Create a New Web Service on Render

1. Go to your Render dashboard
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure the service:

**Basic Settings:**
- **Name**: `neurolearn-backend`
- **Environment**: `Python 3`
- **Region**: Choose closest to your users
- **Branch**: `main` (or your default branch)

**Build & Deploy:**
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python aitutor_backend/wsgi.py`

### 3. Configure Environment Variables

In the Render dashboard, go to Environment tab and add:

**Required Variables:**
```
FLASK_ENV=production
SECRET_KEY=<generate a secure random string>
JWT_SECRET_KEY=<generate a secure random string>
DATABASE_URL=<will be provided by Render PostgreSQL>
PORT=10000
```

**Optional Variables:**
```
FRONTEND_URL=https://your-frontend-url.onrender.com
```

### 4. Create PostgreSQL Database

1. In Render dashboard, click "New +" → "PostgreSQL"
2. Configure:
   - **Name**: `neurolearn-db`
   - **Database**: `neurolearn`
   - **User**: `neurolearn_user`
   - **Plan**: Starter (free tier)

3. Copy the **External Database URL** and add it as `DATABASE_URL` environment variable

### 5. Deploy

1. Click "Create Web Service"
2. Render will automatically build and deploy your application
3. Monitor the build logs for any issues

### 6. Update Frontend Configuration

Update your frontend's API configuration to point to your Render backend:

```javascript
// In your frontend config
const API_BASE_URL = 'https://neurolearn-backend.onrender.com';
```

## Configuration Files Explained

### render.yaml
```yaml
services:
  - type: web
    name: neurolearn-backend
    env: python
    plan: starter
    buildCommand: pip install -r requirements.txt
    startCommand: python aitutor_backend/wsgi.py
    envVars:
      - key: FLASK_ENV
        value: production
    healthCheckPath: /api/auth/health
```

### Procfile
```
web: python aitutor_backend/wsgi.py
```

## Troubleshooting

### Common Issues

1. **Build Failures**
   - Check `requirements.txt` for version conflicts
   - Ensure all dependencies are compatible with Python 3.9+

2. **Database Connection Issues**
   - Verify `DATABASE_URL` is correctly set
   - Check PostgreSQL service is running

3. **CORS Errors**
   - Update `FRONTEND_URL` environment variable
   - Check CORS configuration in `__init__.py`

4. **Health Check Failures**
   - Ensure `/api/auth/health` endpoint is accessible
   - Check application logs for errors

### Monitoring

1. **Logs**: Check Render dashboard → Logs tab
2. **Metrics**: Monitor CPU, memory usage
3. **Health**: Use `/api/auth/health` endpoint

## Production Considerations

### Security
- Use strong, unique `SECRET_KEY` and `JWT_SECRET_KEY`
- Enable HTTPS (automatic on Render)
- Review CORS settings for production

### Performance
- Consider upgrading to paid plan for better performance
- Monitor database connections
- Implement proper logging

### Scaling
- Render auto-scales based on traffic
- Consider database connection pooling for high traffic
- Monitor resource usage

## Environment Variables Reference

| Variable | Required | Description |
|----------|----------|-------------|
| `FLASK_ENV` | Yes | Set to `production` |
| `SECRET_KEY` | Yes | Flask secret key |
| `JWT_SECRET_KEY` | Yes | JWT signing key |
| `DATABASE_URL` | Yes | PostgreSQL connection string |
| `PORT` | Yes | Port number (Render sets this) |
| `FRONTEND_URL` | No | Frontend URL for CORS |

## Next Steps

1. **Deploy Frontend**: Deploy your React/Vue frontend to Render or Vercel
2. **Set up Monitoring**: Configure error tracking (Sentry, etc.)
3. **Backup Strategy**: Set up database backups
4. **Custom Domain**: Configure custom domain if needed

## Support

- Render Documentation: [render.com/docs](https://render.com/docs)
- Render Community: [community.render.com](https://community.render.com)

---

**Note**: This deployment uses Render's free tier. For production applications, consider upgrading to paid plans for better performance and reliability.
