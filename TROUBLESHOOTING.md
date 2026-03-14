"# 🔧 Troubleshooting & FAQ - ProctoringME

## Table of Contents
1. [Installation Issues](#installation-issues)
2. [Database Issues](#database-issues)
3. [Server Issues](#server-issues)
4. [AI/ML Model Issues](#aiml-model-issues)
5. [Email & External Services](#email--external-services)
6. [Browser & Camera Issues](#browser--camera-issues)
7. [Frequently Asked Questions](#frequently-asked-questions)

---

## Installation Issues

### ❌ Problem: \"pip: command not found\"

**Cause:** Python/pip not installed or not in PATH

**Solution:**
```bash
# Check if Python is installed
python --version
python3 --version

# Install pip
python -m ensurepip --upgrade
# OR
python3 -m ensurepip --upgrade
```

**Windows:** Add Python to PATH during installation or reinstall Python with \"Add to PATH\" checked

---

### ❌ Problem: \"ERROR: Failed building wheel for dlib\"

**Cause:** dlib requires C++ compiler and CMake

**Solution (Windows):**
```bash
# Use the provided wheel file
pip install dlib-19.22.99-cp310-cp310-win_amd64.whl
```

**Solution (Linux):**
```bash
# Install build tools
sudo apt-get update
sudo apt-get install build-essential cmake
sudo apt-get install libopenblas-dev liblapack-dev
sudo apt-get install libx11-dev libgtk-3-dev

# Then install dlib
pip install dlib
```

**Solution (macOS):**
```bash
# Install Xcode Command Line Tools
xcode-select --install

# Install cmake
brew install cmake

# Install dlib
pip install dlib
```

---

### ❌ Problem: \"ERROR: No matching distribution found for torch\"

**Cause:** Wrong Python version or platform

**Solution:**
```bash
# Check Python version (must be 3.8-3.11)
python --version

# Install PyTorch separately (CPU version)
pip install torch torchvision torchaudio

# Then install remaining requirements
pip install -r ../requirements.txt
```

**For CUDA/GPU support:**
Visit: https://pytorch.org/get-started/locally/

---

### ❌ Problem: \"Cannot activate virtual environment (Windows PowerShell)\"

**Error:** `execution of scripts is disabled on this system`

**Solution:**
```powershell
# Run PowerShell as Administrator
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Then try activating again
venv\Scripts\activate
```

**Alternative:** Use Command Prompt instead of PowerShell:
```cmd
venv\Scripts\activate.bat
```

---

### ❌ Problem: \"ModuleNotFoundError: No module named 'xyz'\"

**Cause:** Virtual environment not activated or dependencies not installed

**Solution:**
```bash
# Check if venv is activated (should see (venv) in prompt)
# If not, activate it:
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# Reinstall all dependencies
pip install --upgrade pip
pip install -r ../requirements.txt

# Verify specific module
pip list | grep module-name
```

---

## Database Issues

### ❌ Problem: \"django.db.utils.OperationalError: could not connect to server\"

**Cause:** PostgreSQL not running or wrong credentials

**Solution 1 - Check PostgreSQL Status:**

**Windows:**
```cmd
# Open Services (services.msc)
# Look for \"postgresql-x64-XX\"
# Ensure it's running

# Or use command:
pg_ctl status -D \"C:\Program Files\PostgreSQL\XX\data\"
```

**Linux:**
```bash
# Check status
sudo systemctl status postgresql

# If not running, start it
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

**macOS:**
```bash
# Check status
brew services list

# Start PostgreSQL
brew services start postgresql
```

**Solution 2 - Verify Credentials:**
```bash
# Test connection manually
psql -U futur_user -d futurproctor_db -h localhost

# If this fails, your .env credentials don't match PostgreSQL
```

---

### ❌ Problem: \"database 'futurproctor_db' does not exist\"

**Cause:** Database not created in PostgreSQL

**Solution:**
```bash
# Login to PostgreSQL
sudo -u postgres psql  # Linux/macOS
# OR use SQL Shell on Windows

# Create database
CREATE DATABASE futurproctor_db;

# Create user if not exists
CREATE USER futur_user WITH PASSWORD '12345678';

# Grant privileges
GRANT ALL PRIVILEGES ON DATABASE futurproctor_db TO futur_user;

# Exit
\q
```

---

### ❌ Problem: \"relation 'xyz' does not exist\"

**Cause:** Database migrations not applied

**Solution:**
```bash
# Apply all migrations
python manage.py migrate

# If issues persist, check migration status
python manage.py showmigrations

# If you see [ ] (unchecked), apply them
python manage.py migrate

# If problems continue, delete migration files and recreate
# ⚠️ WARNING: This will delete data!
# rm proctoring/migrations/0*.py
# python manage.py makemigrations
# python manage.py migrate
```

---

### ❌ Problem: \"password authentication failed for user\"

**Cause:** Wrong password in .env file

**Solution:**
```bash
# Option 1: Update PostgreSQL password to match .env
sudo -u postgres psql
ALTER USER futur_user WITH PASSWORD '12345678';
\q

# Option 2: Update .env to match PostgreSQL password
# Edit .env file and change DB_PASSWORD
```

---

## Server Issues

### ❌ Problem: \"Error: That port is already in use\"

**Cause:** Another process using port 8000

**Solution 1 - Use Different Port:**
```bash
python manage.py runserver 8080
# Access at: http://127.0.0.1:8080/
```

**Solution 2 - Kill Process Using Port 8000:**

**Linux/macOS:**
```bash
# Find process
lsof -i :8000
# OR
netstat -tulpn | grep 8000

# Kill process (replace PID with actual process ID)
kill -9 PID
```

**Windows:**
```cmd
# Find process
netstat -ano | findstr :8000

# Kill process (replace PID with actual process ID)
taskkill /PID PID /F
```

---

### ❌ Problem: \"DisallowedHost at /\"

**Error:** `Invalid HTTP_HOST header: 'xyz'. You may need to add 'xyz' to ALLOWED_HOSTS.`

**Solution:**
```python
# Edit futurproctor/settings.py
ALLOWED_HOSTS = ['*']  # Already set, but verify

# If deploying to production, use specific domains:
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com', '127.0.0.1', 'localhost']
```

---

### ❌ Problem: \"Static files not loading (CSS/JS missing)\"

**Cause:** Static files not collected or incorrect configuration

**Solution:**
```bash
# Collect static files
python manage.py collectstatic --clear --no-input

# For development, ensure DEBUG=True in .env
# Check settings.py for STATIC_URL and STATIC_ROOT
```

**Quick Fix for Development:**
```python
# In settings.py, verify these settings:
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = []

# Ensure WhiteNoise is in MIDDLEWARE (already configured)
```

---

### ❌ Problem: \"CSRF verification failed\"

**Error:** `Forbidden (403) CSRF verification failed. Request aborted.`

**Solution:**
```python
# 1. Ensure {% csrf_token %} is in all forms
# In your template:
<form method=\"POST\">
    {% csrf_token %}
    ...
</form>

# 2. Check MIDDLEWARE in settings.py has:
'django.middleware.csrf.CsrfViewMiddleware',

# 3. For API requests, include CSRF token in headers
# In JavaScript:
const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
fetch('/api/endpoint/', {
    method: 'POST',
    headers: {
        'X-CSRFToken': csrftoken,
    },
    ...
});
```

---

## AI/ML Model Issues

### ❌ Problem: \"FileNotFoundError: yolo11s.pt not found\"

**Cause:** Working directory is wrong or file is missing

**Solution:**
```bash
# Verify file exists
ls -la yolo11s.pt  # Should show 19MB file

# If missing, download YOLO model
# The project includes it, but if deleted:
# Download from Ultralytics or use model auto-download

# Ensure you're in the correct directory
cd /path/to/ProctoringME/futurproctor
python manage.py runserver
```

---

### ❌ Problem: \"Face detection not working\"

**Cause:** Camera not accessible or face_recognition library issues

**Solution:**
```bash
# Test face_recognition installation
python -c \"import face_recognition; print('OK')\"

# If error, reinstall dependencies
pip install --upgrade face-recognition
pip install --upgrade dlib

# Linux: Install additional libraries
sudo apt-get install libopencv-dev python3-opencv
```

**Browser Permission:**
- Grant camera access when prompted
- Check browser settings (chrome://settings/content/camera)

---

### ❌ Problem: \"OpenCV error: can't open camera\"

**Cause:** Camera in use or permission denied

**Solution:**

**Windows:**
- Close other apps using camera (Skype, Teams, Zoom)
- Check Privacy Settings → Camera → Allow desktop apps

**Linux:**
```bash
# Add user to video group
sudo usermod -a -G video $USER

# Logout and login again
# Or: newgrp video

# Check camera devices
ls -la /dev/video*

# Test with OpenCV
python -c \"import cv2; cap = cv2.VideoCapture(0); print('OK' if cap.isOpened() else 'FAIL')\"
```

**macOS:**
- System Preferences → Security & Privacy → Camera
- Allow Terminal/PyCharm/VS Code to access camera

---

### ❌ Problem: \"CUDA out of memory\" or \"torch.cuda is not available\"

**Cause:** PyTorch trying to use GPU but not configured properly

**Solution:**
```bash
# Force CPU usage (add to settings or model code)
import torch
device = torch.device('cpu')

# Or set environment variable before running
export CUDA_VISIBLE_DEVICES=\"\"  # Linux/macOS
set CUDA_VISIBLE_DEVICES=      # Windows

# Then run server
python manage.py runserver
```

---

## Email & External Services

### ❌ Problem: \"SMTPAuthenticationError\"

**Cause:** Wrong email credentials or less secure app access disabled

**Gmail Solution:**
1. Enable 2-Factor Authentication
2. Generate App Password: https://myaccount.google.com/apppasswords
3. Use App Password in .env (not regular password)

```env
EMAIL_HOST_USER=youremail@gmail.com
EMAIL_HOST_PASSWORD=abcd efgh ijkl mnop  # 16-char app password
```

**Outlook/Hotmail:**
```env
EMAIL_HOST=smtp-mail.outlook.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
```

---

### ❌ Problem: \"GROQ API error\"

**Cause:** Invalid API key or service unavailable

**Solution:**
```bash
# Test GROQ service
python test_sendgrid.py

# Or in Django shell
python manage.py shell
>>> from proctoring.groq_service import test_groq
>>> test_groq()

# Get new API key: https://console.groq.com/keys
# Update in .env
GROQ_API_KEY=your-new-key-here
```

---

## Browser & Camera Issues

### ❌ Problem: \"Camera permission denied in browser\"

**Solution:**

**Chrome:**
1. Click lock icon in address bar
2. Camera → Allow
3. Refresh page

**Firefox:**
1. Click camera icon with slash in address bar
2. Select \"Allow\"
3. Refresh page

**Safari:**
1. Safari → Preferences → Websites → Camera
2. Allow for 127.0.0.1
3. Refresh page

---

### ❌ Problem: \"Page not loading / timeout\"

**Cause:** Server not running or wrong URL

**Checklist:**
```bash
# 1. Server is running?
# Should see: \"Starting development server at http://127.0.0.1:8000/\"

# 2. Correct URL?
# Use: http://127.0.0.1:8000/
# NOT: http://localhost:8000/ (sometimes different)

# 3. Check firewall
# Windows: Allow Python through firewall
# Linux: sudo ufw allow 8000

# 4. Check terminal for errors
# Look for Python exceptions in server output
```

---

### ❌ Problem: \"Real-time features not working (WebSocket)\"

**Cause:** Channels not configured or Redis not running

**Solution:**
```bash
# Check if channels is installed
pip install channels channels-redis

# Install Redis (required for WebSocket)
# Windows: https://github.com/microsoftarchive/redis/releases
# Linux: sudo apt-get install redis-server
# macOS: brew install redis

# Start Redis
# Linux: sudo systemctl start redis
# macOS: brew services start redis
# Windows: redis-server.exe

# Uncomment channels in settings.py INSTALLED_APPS
```

---

## Frequently Asked Questions

### Q1: Can I use SQLite instead of PostgreSQL?

**A:** Yes, for testing only. Not recommended for production.

```python
# In settings.py, temporarily change:
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

---

### Q2: How do I reset my admin password?

**A:**
```bash
python manage.py changepassword admin

# Or create new superuser
python manage.py createsuperuser
```

---

### Q3: Can I run this on a different port?

**A:** Yes:
```bash
# Development
python manage.py runserver 0.0.0.0:8080

# Access from other devices on network:
http://YOUR_IP:8080/
```

---

### Q4: How do I clear the database and start fresh?

**A:**
```bash
# ⚠️ WARNING: This deletes all data!

# Method 1: Drop and recreate database
sudo -u postgres psql
DROP DATABASE futurproctor_db;
CREATE DATABASE futurproctor_db;
GRANT ALL PRIVILEGES ON DATABASE futurproctor_db TO futur_user;
\q

# Then re-run migrations
python manage.py migrate

# Method 2: Delete SQLite (if using it)
rm db.sqlite3
python manage.py migrate
```

---

### Q5: Can I deploy this to production?

**A:** Yes, but requires additional configuration:

**Production Checklist:**
- [ ] Set `DEBUG=False` in .env
- [ ] Generate new `SECRET_KEY`
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Use strong database password
- [ ] Set up HTTPS/SSL
- [ ] Configure static files with WhiteNoise or CDN
- [ ] Use production WSGI server (Gunicorn, uWSGI)
- [ ] Set up process manager (Supervisor, systemd)
- [ ] Configure reverse proxy (Nginx, Apache)
- [ ] Set up monitoring and logging
- [ ] Regular backups of database

**Quick Production Server:**
```bash
# Install Gunicorn
pip install gunicorn

# Run with Gunicorn
gunicorn futurproctor.wsgi:application --bind 0.0.0.0:8000
```

---

### Q6: How do I update Python dependencies?

**A:**
```bash
# Activate virtual environment
source venv/bin/activate

# Update all packages
pip install --upgrade -r ../requirements.txt

# Or update specific package
pip install --upgrade django

# Freeze to requirements
pip freeze > ../requirements.txt
```

---

### Q7: Where are the log files?

**A:** By default, Django logs to console (terminal output).

To add file logging, add to `settings.py`:
```python
LOGGING = {
    'version': 1,
    'handlers': {
        'file': {
            'class': 'logging.FileHandler',
            'filename': 'debug.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'DEBUG',
        },
    },
}
```

---

### Q8: Can I use Python 3.11 or 3.12?

**A:** Possibly, but not tested. Some dependencies (especially dlib) may have issues.

**Recommended:** Use Python 3.10 for best compatibility.

---

### Q9: How do I backup the database?

**A:**
```bash
# Backup PostgreSQL database
pg_dump -U futur_user -d futurproctor_db > backup_$(date +%Y%m%d).sql

# Restore from backup
psql -U futur_user -d futurproctor_db < backup_20250308.sql

# Django's way (creates JSON)
python manage.py dumpdata > backup.json

# Restore Django backup
python manage.py loaddata backup.json
```

---

### Q10: How do I contribute or modify the code?

**A:**
```bash
# 1. Create a new branch
git checkout -b feature-name

# 2. Make changes

# 3. Test thoroughly

# 4. Commit changes
git add .
git commit -m \"Description of changes\"

# 5. Push to your fork
git push origin feature-name

# 6. Create Pull Request on GitHub
```

---

## Getting More Help

### Check Logs First
```bash
# Terminal output where runserver is running shows:
# - Request logs
# - Error tracebacks
# - Database queries (if DEBUG=True)
```

### Use Django Shell for Debugging
```bash
python manage.py shell

>>> from proctoring.models import *
>>> # Test your models and functions interactively
```

### Django Debug Mode
With `DEBUG=True`, you get detailed error pages showing:
- Full traceback
- Local variables
- Request information
- Settings (without secrets)

### Community Resources
- **Django Documentation:** https://docs.djangoproject.com/
- **Stack Overflow:** Tag your questions with `django`, `postgresql`, `opencv`
- **Django Forum:** https://forum.djangoproject.com/
- **Project Issues:** https://github.com/vikrantan5/ProctoringME/issues

---

## Emergency Reset Procedure

If everything is broken and you want to start fresh:

```bash
# 1. Backup any important data first!

# 2. Deactivate and delete virtual environment
deactivate
rm -rf venv/  # Linux/macOS
# OR
rmdir /s venv  # Windows

# 3. Drop and recreate database
sudo -u postgres psql
DROP DATABASE futurproctor_db;
CREATE DATABASE futurproctor_db;
GRANT ALL PRIVILEGES ON DATABASE futurproctor_db TO futur_user;
\q

# 4. Recreate virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate

# 5. Reinstall everything
pip install --upgrade pip
pip install -r ../requirements.txt

# 6. Fresh migrations
python manage.py migrate

# 7. Create superuser
python manage.py createsuperuser

# 8. Start fresh
python manage.py runserver
```

---

**Still stuck? Double-check the EXECUTION_GUIDE.md for step-by-step instructions!**
"