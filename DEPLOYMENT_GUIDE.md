# DEPLOYMENT & PRODUCTION GUIDE

Guide for deploying the Fingerprint Blood Group Detection System to production.

## Table of Contents
1. Pre-Deployment Checklist
2. Local Production Testing
3. Server Deployment
4. Security Hardening
5. Monitoring & Maintenance
6. Troubleshooting

---

## Pre-Deployment Checklist

### Code Quality
- [ ] All code commented and documented
- [ ] No debug print statements
- [ ] Error handling implemented
- [ ] Input validation complete
- [ ] Code tested thoroughly

### Security
- [ ] Change `debug=False` in app.py
- [ ] Remove hardcoded credentials
- [ ] Implement HTTPS/SSL
- [ ] Add authentication layer
- [ ] Enable CORS restrictions
- [ ] Add rate limiting
- [ ] Input sanitization tested
- [ ] SQL injection prevention verified
- [ ] XSS prevention verified

### Database
- [ ] Database backed up
- [ ] Indexes created for performance
- [ ] Database connection pooling set up
- [ ] Backup automation configured
- [ ] Migration scripts tested

### Documentation
- [ ] README.md updated
- [ ] API documentation complete
- [ ] Deployment instructions clear
- [ ] Troubleshooting guide created
- [ ] Change log updated

### Testing
- [ ] All unit tests passing
- [ ] Integration tests passing
- [ ] Load testing completed
- [ ] Security testing completed
- [ ] User acceptance testing done

---

## Local Production Testing

### Step 1: Disable Debug Mode

Edit `backend/app.py`:
```python
if __name__ == '__main__':
    app.run(
        host='127.0.0.1',
        port=5000,
        debug=False  # Change from True to False
    )
```

### Step 2: Test All Endpoints

```bash
# Test API status
curl http://localhost:5000/

# Test registration
curl -X POST http://localhost:5000/api/register \
  -F "name=Test" \
  -F "blood_group=O+" \
  -F "fingerprint_image=@test.jpg"

# Test verification
curl -X POST http://localhost:5000/api/verify \
  -F "fingerprint_image=@test.jpg"

# Test users list
curl http://localhost:5000/api/users
```

### Step 3: Load Testing

Use Apache Bench or similar tools:
```bash
# Install Apache Bench (if not installed)
# macOS: brew install httpd
# Windows: Download from Apache

# Test 100 requests with 10 concurrent
ab -n 100 -c 10 http://localhost:5000/
```

### Step 4: Security Testing

Test for common vulnerabilities:
```bash
# Test SQL Injection
curl -X POST http://localhost:5000/api/register \
  -F 'name=" OR 1=1 --' \
  -F "blood_group=O+" \
  -F "fingerprint_image=@test.jpg"

# Test XSS
curl -X POST http://localhost:5000/api/register \
  -F 'name=<script>alert("xss")</script>' \
  -F "blood_group=O+" \
  -F "fingerprint_image=@test.jpg"
```

---

## Server Deployment

### Option 1: Deploy on PythonAnywhere

**Step 1: Create Account**
- Visit [www.pythonanywhere.com](https://www.pythonanywhere.com)
- Create free or paid account

**Step 2: Upload Files**
```bash
# Via git
git clone <your-repo-url>

# Or via Web interface
# Upload folder structure
```

**Step 3: Create Virtual Environment**
```bash
mkvirtualenv --python=/usr/bin/python3.9 fingerprint
pip install -r requirements.txt
```

**Step 4: Configure Web App**
- Go to Web section
- Add new web app
- Choose Python 3.9 + Flask
- Set virtual environment path
- Configure WSGI file

**Step 5: Set WSGI Configuration**
Create or edit `wsgi_file`:
```python
import sys
sys.path.insert(0, '/home/username/fingerprint')

from backend.app import app as application
```

**Step 6: Reload Web App**
- Click "Reload" button
- Test at `https://username.pythonanywhere.com`

### Option 2: Deploy on Heroku

**Step 1: Install Heroku CLI**
```bash
# macOS
brew tap heroku/brew && brew install heroku

# Windows
# Download from https://devcenter.heroku.com/articles/heroku-cli
```

**Step 2: Login to Heroku**
```bash
heroku login
```

**Step 3: Create Procfile**
Create `Procfile` in project root:
```
web: gunicorn backend.app:app
```

**Step 4: Create requirements.txt**
Add gunicorn:
```
Flask==2.3.0
Flask-CORS==4.0.0
opencv-python==4.7.0
numpy==1.24.0
Werkzeug==2.3.0
gunicorn==20.1.0
```

**Step 5: Initialize Git**
```bash
git init
git add .
git commit -m "Initial commit"
```

**Step 6: Create Heroku App**
```bash
heroku create fingerprint-app
```

**Step 7: Deploy**
```bash
git push heroku main
```

**Step 8: View Logs**
```bash
heroku logs --tail
```

### Option 3: Deploy on AWS EC2

**Step 1: Launch EC2 Instance**
- Instance type: t2.micro (free tier)
- OS: Ubuntu 20.04 LTS
- Security group: Allow ports 80, 443, 5000

**Step 2: SSH into Instance**
```bash
ssh -i your-key.pem ec2-user@your-instance-ip
```

**Step 3: Install Dependencies**
```bash
sudo apt update
sudo apt install python3-pip python3-venv
sudo apt install nginx
```

**Step 4: Upload Project**
```bash
scp -i your-key.pem -r fingerprint-app ec2-user@your-ip:/home/ec2-user/
```

**Step 5: Setup Virtual Environment**
```bash
cd fingerprint-app/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Step 6: Run with Gunicorn**
```bash
gunicorn --workers 4 --bind 0.0.0.0:5000 app:app
```

**Step 7: Configure Nginx**
Edit `/etc/nginx/sites-available/default`:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /frontend {
        alias /home/ec2-user/fingerprint-app/frontend;
    }
}
```

**Step 8: Restart Nginx**
```bash
sudo systemctl restart nginx
```

### Option 4: Deploy using Docker

**Step 1: Create Dockerfile**
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY backend/requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "backend/app.py"]
```

**Step 2: Create Docker Compose**
```yaml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - ./backend/database.db:/app/backend/database.db
    environment:
      - FLASK_ENV=production
```

**Step 3: Build and Run**
```bash
docker-compose up -d
```

---

## Security Hardening

### 1. Enable HTTPS

**Using Let's Encrypt:**
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get certificate
sudo certbot certonly --nginx -d your-domain.com

# Auto-renew
sudo systemctl enable certbot.timer
```

### 2. Add Authentication

Update `backend/app.py`:
```python
from functools import wraps
from flask import request

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if not api_key or api_key != os.environ.get('API_KEY'):
            return jsonify({'status': 'error', 'message': 'Invalid API key'}), 401
        return f(*args, **kwargs)
    return decorated_function

@app.route('/api/register', methods=['POST'])
@require_api_key
def register():
    # ... existing code
```

### 3. Add Rate Limiting

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

@app.route('/api/register', methods=['POST'])
@limiter.limit("10 per hour")
def register():
    # ... existing code
```

### 4. Enable CORS Restrictions

```python
CORS(app, resources={
    r"/api/*": {
        "origins": ["https://yourdomain.com"],
        "methods": ["GET", "POST"]
    }
})
```

### 5. Set Security Headers

```python
@app.after_request
def set_security_headers(response):
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    return response
```

### 6. Database Security

```python
# Use environment variables for sensitive data
import os

DB_PASSWORD = os.environ.get('DB_PASSWORD')
DB_USER = os.environ.get('DB_USER')
```

---

## Monitoring & Maintenance

### 1. Set Up Logging

```python
import logging

logging.basicConfig(
    filename='app.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

@app.route('/api/register', methods=['POST'])
def register():
    logger.info(f'Registration attempt: {name}')
    # ... rest of code
```

### 2. Monitor Performance

Use tools like:
- **New Relic**: APM monitoring
- **Datadog**: Infrastructure monitoring
- **Prometheus**: Metrics collection
- **ELK Stack**: Log analysis

### 3. Database Backups

**Automated Backup Script:**
```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)

cp /path/to/database.db "$BACKUP_DIR/database_$DATE.db"

# Keep only last 30 days
find $BACKUP_DIR -mtime +30 -delete
```

**Schedule with Cron:**
```bash
# Backup every day at 2 AM
0 2 * * * /path/to/backup.sh
```

### 4. System Monitoring

```bash
# Monitor CPU/Memory
top

# Check disk space
df -h

# Monitor network
netstat -tuln
```

### 5. Log Rotation

Configure logrotate:
```bash
# /etc/logrotate.d/fingerprint

/path/to/app.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    missingok
}
```

---

## Performance Optimization

### 1. Database Indexing

```python
# Add to database.py
cursor.execute('CREATE INDEX idx_fingerprint_hash ON users(fingerprint_hash)')
cursor.execute('CREATE INDEX idx_blood_group ON users(blood_group)')
```

### 2. Caching

```python
from flask_caching import Cache

cache = Cache(app, config={'CACHE_TYPE': 'simple'})

@app.route('/api/users')
@cache.cached(timeout=300)  # Cache for 5 minutes
def get_users():
    # ... existing code
```

### 3. Connection Pooling

```python
from sqlalchemy import create_engine

engine = create_engine(
    'sqlite:///database.db',
    pool_pre_ping=True,
    pool_recycle=3600
)
```

### 4. Image Optimization

```python
# In fingerprint.py
from PIL import Image

# Compress image before processing
img.save(output, quality=85, optimize=True)
```

---

## Disaster Recovery

### 1. Backup Strategy

- Daily automated backups
- Weekly full backups
- Monthly archive backups
- Off-site backup storage

### 2. Recovery Plan

- Test restore process monthly
- Document recovery steps
- Maintain backup inventory
- Monitor backup integrity

### 3. Health Checks

```bash
# Health check script
#!/bin/bash

if curl -f http://localhost:5000/ > /dev/null 2>&1; then
    echo "API is healthy"
else
    echo "API is down - sending alert"
    # Send alert email/SMS
fi
```

---

## Scaling Considerations

### Vertical Scaling (Upgrade Hardware)
- Increase CPU cores
- Increase RAM
- Faster storage (SSD)

### Horizontal Scaling (Multiple Servers)
- Load balancer (Nginx, HAProxy)
- Multiple Flask instances
- Shared database (PostgreSQL)
- Redis for caching

### Load Balancer Configuration

```nginx
upstream flask_app {
    server 127.0.0.1:5000;
    server 127.0.0.1:5001;
    server 127.0.0.1:5002;
}

server {
    listen 80;
    
    location / {
        proxy_pass http://flask_app;
        proxy_set_header Host $host;
    }
}
```

---

## Troubleshooting Deployment

### Issue: Port Already in Use

```bash
# Find process using port 5000
lsof -i :5000

# Kill process
kill -9 <PID>

# Or use different port
gunicorn --bind 0.0.0.0:8000 app:app
```

### Issue: Permission Denied

```bash
# Check file permissions
ls -la database.db

# Fix permissions
chmod 644 database.db
chmod 755 backend/
```

### Issue: Module Not Found

```bash
# Verify virtual environment is activated
which python

# Reinstall dependencies
pip install -r requirements.txt

# Check installed packages
pip list
```

### Issue: Database Locked

```python
# Add timeout in database.py
conn = sqlite3.connect(DB_PATH, timeout=10.0)
```

### Issue: High Memory Usage

```bash
# Monitor memory
free -h

# Identify memory leaks with profiler
python -m memory_profiler app.py
```

---

## Post-Deployment Checklist

- [ ] All endpoints tested in production
- [ ] HTTPS working correctly
- [ ] Database backups automated
- [ ] Monitoring active
- [ ] Logging configured
- [ ] Error alerts configured
- [ ] Performance metrics baseline established
- [ ] Security audit completed
- [ ] Documentation updated
- [ ] Team trained on deployment

---

## Support & Updates

### Regular Maintenance
- Update dependencies monthly
- Security patches immediately
- Test updates in staging first
- Monitor for known vulnerabilities

### Update Process
```bash
# Check for outdated packages
pip list --outdated

# Update packages
pip install --upgrade package_name

# Test thoroughly
pytest tests/

# Deploy to production
```

---

**Deployment Guide Complete**
