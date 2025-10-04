# Deployment Guide

## Overview

This guide covers deploying NeuroLearn across different platforms including Render, Vercel, Netlify, and Docker containers. The deployment strategy supports both development and production environments.

## Environment Setup

### Backend Environment Variables

Create a `.env` file in the backend directory:

```bash
# Backend Environment Configuration
FLASK_ENV=production
DATABASE_URL=postgresql://user:password@host:port/database
SECRET_KEY=your-super-secret-key-here
JWT_SECRET_KEY=your-jwt-secret

# External Services
OPENAI_API_KEY=your-openai-api-key
REDIS_URL=redis://localhost:6379

# Model Paths
EMOTION_MODEL_PATH=models/emotion_model.h5
ADAPTIVE_MODEL_PATH=models/adaptive_model.pkl

# CORS Configuration
ALLOWED_ORIGINS=https://your-frontend-domain.com,https://localhost:3000

# Rate Limiting
RATELIMIT_STORAGE_URL=redis://localhost:6379

# Security
BCRYPT_LOG_ROUNDS=12
```

### Frontend Environment Variables

Create a `.env.production` file in frontend/dashboard:

```bash
# Frontend Production Environment
VITE_API_URL=https://your-backend-api.com/api/v1
VITE_WEBSOCKET_URL=wss://your-backend-api.com/ws

# Analytics (Optional)
VITE_GOOGLE_ANALYTICS_ID=GA-XXXXXXXXXX
VITE_SENTRY_DSN=your-sentry-dsn

# Feature Flags
VITE_ENABLE_EMOTION_DETECTION=true
VITE_ENABLE_GAMIFICATION=true
```

## Render Deployment

### Backend Deployment on Render

1. **Create render.yaml configuration:**

The `deployment/render.yaml` file provides service definitions:

```yaml
services:
  - type: web
    name: neurolearn-backend
    env: python
    region: oregon
    plan: standard
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn --bind 0.0.0.0:$PORT wsgi:application
    envVars:
      - key: FLASK_ENV
        value: production
      - key: DATABASE_URL
        fromDatabase:
          name: neurolearn-db
          property: connectionString
      - key: SECRET_KEY
        generateValue: true
    healthCheckPath: /health
    autoDeploy: true

databases:
  - name: neurolearn-db
    databaseName: neurolearn
    user: neurolearn_user
    region: oregon
    plan: standard
```

2. **Deploy via Render Dashboard:**
   - Connect your GitHub repository
   - Select the `render.yaml` file for automatic configuration
   - Set environment variables
   - Deploy the service

### Frontend Deployment on Render

1. **Configure build settings:**
   - Build Command: `cd frontend/dashboard && npm install && npm run build`
   - Publish Directory: `frontend/dashboard/dist`
   - Environment: Node.js

2. **Set environment variables:**
   - `VITE_API_URL`: Your Render backend URL
   - `VITE_WEBSOCKET_URL`: WebSocket URL for your backend

## Vercel Deployment

### Frontend on Vercel

1. **Create vercel.json:**

```json
{
  "version": 2,
  "builds": [
    {
      "src": "frontend/dashboard/package.json",
      "use": "@vercel/node"
    }
  ],
  "routes": [
    {
      "src": "/frontend/dashboard/(.*)",
      "dest": "/frontend/dashboard/$1"
    },
    {
      "src": "/(.*)",
      "dest": "/frontend/dashboard/$1"
    }
  ],
  "env": {
    "VITE_API_URL": "https://neurolearn-backend.herokuapp.com",
    "VITE_WEBSOCKET_URL": "wss://neurolearn-backend.herokuapp.com/ws"
  }
}
```

2. **Deploy Steps:**
   - Connect GitHub repository to Vercel
   - Set framework preset to Vite
   - Configure environment variables
   - Deploy

### Backend on Vercel (Serverless)

Create `api/` directory for serverless functions:

```python
# api/emotion.py - Vercel serverless function
from aitutor_backend import create_app

app = create_app()

def handler(request):
    return app(request.environ['REQUEST_URI'], 
               request.environ['REQUEST_METHOD'], 
               request.body)
```

## Netlify Deployment

### Frontend on Netlify

1. **Create netlify.toml:**

```toml
[build]
  publish = "frontend/dashboard/dist"
  command = "cd frontend/dashboard && npm install && npm run build"

[build.environment]
  NODE_VERSION = "18"
  VITE_API_URL = "https://neurolearn-backend.herokuapp.com"

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200

[[headers]]
  for = "/static/*"
  [headers.values]
    Cache-Control = "public, max-age=31536000"

[context.production.environment]
  VITE_API_URL = "https://api.neurolearn.com"
  VITE_WEBSOCKET_URL = "wss://api.neurolearn.com/ws"
```

2. **Deploy Steps:**
   - Connect GitHub repository
   - Set build command and publish directory
   - Configure environment variables
   - Enable automatic deployments

## Docker Deployment

### Backend Dockerfile

```dockerfile
# backend/Dockerfile
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY aitutor_backend/ .
COPY Face-Emotion-Detector/ Face-Emotion-Detector/

# Create models directory
RUN mkdir -p models

# Set environment variables
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Start application
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--worker-class", "gevent", "wsgi:application"]
```

### Frontend Dockerfile

```dockerfile
# frontend/Dockerfile
FROM node:18-alpine as builder

WORKDIR /app

# Copy package files
COPY frontend/dashboard/package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy source code
COPY frontend/dashboard/ .

# Build application
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built application
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY frontend/dashboard/nginx.conf /etc/nginx/nginx.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

### Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "5000:5000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/neurolearn
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis
    volumes:
      - ./models:/app/models

  frontend:
    build: ./frontend
    ports:
      - "3000:80"
    environment:
      - VITE_API_URL=http://localhost:5000
    depends_on:
      - backend

  db:
    image: postgres:14
    environment:
      POSTGRES_DB: neurolearn
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

## Production Optimization

### Database Optimization

1. **Connection Pooling:**

```python
# Database configuration for production
SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_size': 20,
    'max_overflow': 30,
    'pool_pre_ping': True,
    'pool_recycle': 3600,
    'pool_timeout': 20
}
```

2. **Query Optimization:**

```python
# Enable query caching
from flask_caching import Cache

cache = Cache(app, config={
    'CACHE_TYPE': 'redis',
    'CACHE_REDIS_URL': 'redis://localhost:6379'
})

@cache.memoize(timeout=300)
def get_user_profile(user_id):
    return User.query.get(user_id)
```

### Performance Monitoring

1. **Application Performance Monitoring:**

```python
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

sentry_sdk.init(
    dsn="YOUR_SENTRY_DSN",
    integrations=[FlaskIntegration()],
    traces_sample_rate=1.0
)
```

2. **Database Monitoring:**

```python
# Query performance monitoring
from flask_sqlalchemy import SQLAlchemy
import logging

logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
```

## SSL/TLS Configuration

### Let's Encrypt with Certbot

```bash
# Install certbot
sudo apt-get install certbot python3-certbot-nginx

# Obtain SSL certificate
sudo certbot --nginx -d yourdomain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

### Nginx Configuration

```nginx
# nginx.conf
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /ws {
        proxy_pass http://localhost:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

## Database Migrations

### Configure Alembic

```python
# alembic/env.py
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from flask import current_app
import logging

config = context.config
config.set_main_option('sqlalchemy.url', 
                      current_app.config['SQLALCHEMY_DATABASE_URI'])

target_metadata = current_app.extensions['migrate'].db.metadata
```

### Migration Commands

```bash
# Initialize Alembic
flask db init

# Create migration
flask db migrate -m "Description of changes"

# Apply migration
flask db upgrade

# Rollback migration
flask db downgrade
```

## Monitoring and Logging

### Application Logging

```python
# Configure production logging
import logging
from logging.handlers import RotatingFileHandler

if not app.debug:
    file_handler = RotatingFileHandler('logs/app.log', 
                                      maxBytes=10240, 
                                      backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(path)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
```

### Health Checks

```python
@app.route('/health')
def health_check():
    """Health check endpoint for load balancers"""
    
    try:
        # Check database connection
        db.session.execute('SELECT 1')
        
        # Check Redis connection
        redis_client.ping()
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow(),
            'version': '1.0.0'
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.utcnow()
        }), 503
```

## Troubleshooting

### Common Issues

1. **Database Connection Errors:**
   - Check connection string format
   - Verify database credentials
   - Ensure database server is accessible

2. **WebSocket Connection Issues:**
   - Check firewall settings
   - Verify proxy configuration
   - Ensure WebSocket support in hosting platform

3. **Build Failures:**
   - Check Node.js and Python versions
   - Verify all dependencies are listed
   - Review build logs for specific errors

### Debug Mode

```python
# Enable debug mode for troubleshooting
if os.environ.get('DEBUG_MODE'):
    app.config['DEBUG'] = True
    app.config['TESTING'] = True
    logging.getLogger().setLevel(logging.DEBUG)
```

## Security Checklist

- [ ] Environment variables properly secured
- [ ] Database credentials encrypted
- [ ] HTTPS enforced
- [ ] CORS configured correctly
- [ ] Rate limiting enabled
- [ ] Input validation implemented
- [ ] SQL injection prevention
- [ ] XSS protection enabled
- [ ] CSRF protection active
- [ ] Dependency vulnerabilities checked

## Backup Strategy

### Database Backups

```bash
# Daily backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump $DATABASE_URL > backup_${DATE}.sql
aws s3 cp backup_${DATE}.sql s3://your-backup-bucket/
```

### Application Data Backups

```python
# Automated backup of stored models and data
import shutil
import boto3

def backup_application_data():
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Create backup archive
    shutil.make_archive(f'app_backup_{timestamp}', 
                       'zip', 'data/')
    
    # Upload to cloud storage
    s3_client = boto3.client('s3')
    s3_client.upload_file(f'app_backup_{timestamp}.zip',
                         'neurolearn-backups',
                         f'backups/{timestamp}.zip')
```
