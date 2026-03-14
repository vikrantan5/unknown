"# 📊 Quick Reference Cheat Sheet - ProctoringME

## 🚀 Setup Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    1. CLONE REPOSITORY                      │
│  git clone https://github.com/vikrantan5/ProctoringME.git  │
│  cd ProctoringME/futurproctor                               │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              2. CREATE VIRTUAL ENVIRONMENT                  │
│  python -m venv venv                                        │
│  source venv/bin/activate (Linux/macOS)                     │
│  venv\Scripts\activate (Windows)                            │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              3. INSTALL DEPENDENCIES                        │
│  pip install --upgrade pip                                  │
│  pip install -r ../requirements.txt                         │
│  (Takes 10-15 minutes)                                      │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              4. SETUP POSTGRESQL DATABASE                   │
│  sudo -u postgres psql                                      │
│  CREATE DATABASE futurproctor_db;                           │
│  CREATE USER futur_user WITH PASSWORD '12345678';           │
│  GRANT ALL PRIVILEGES ON DATABASE futurproctor_db TO futur_user; │
│  \q                                                         │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              5. CREATE .env FILE                            │
│  touch .env (Linux/macOS) or type nul > .env (Windows)     │
│  Add: DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT      │
│  See ENVIRONMENT_CONFIG.md for template                     │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              6. APPLY DATABASE MIGRATIONS                   │
│  python manage.py migrate                                   │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              7. CREATE ADMIN USER                           │
│  python manage.py createsuperuser                           │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              8. START SERVER                                │
│  python manage.py runserver                                 │
│  Access: http://127.0.0.1:8000/                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 📁 Directory Structure at a Glance

```
ProctoringME/
├── 📄 EXECUTION_GUIDE.md      ← Start here for detailed setup
├── 📄 QUICK_START.md          ← Quick 5-step guide
├── 📄 PROJECT_STRUCTURE.md    ← Understand file organization
├── 📄 ENVIRONMENT_CONFIG.md   ← .env file setup
├── 📄 TROUBLESHOOTING.md      ← Fix common issues
├── 📄 requirements.txt        ← Python dependencies
└── 📁 futurproctor/           ← YOUR WORKING DIRECTORY
    ├── 📄 manage.py           ← Main Django management script
    ├── 📄 .env               ← Create this (DB credentials)
    ├── 📁 venv/              ← Create this (virtual environment)
    ├── 📁 futurproctor/      ← Django project config
    │   ├── settings.py       ← Main settings
    │   └── urls.py           ← Main URL routing
    └── 📁 proctoring/        ← Main application
        ├── models.py         ← Database models
        ├── views.py          ← Application logic
        ├── urls.py           ← App URL routing
        ├── 📁 templates/     ← HTML files
        └── 📁 static/        ← CSS, JS, Images
```

---

## 🎯 Essential Commands

### Environment Management
```bash
# Create virtual environment
python -m venv venv

# Activate (do this EVERY TIME you open terminal)
source venv/bin/activate        # Linux/macOS
venv\Scripts\activate           # Windows

# Deactivate
deactivate

# Check if activated (should show venv path)
which python                    # Linux/macOS
where python                    # Windows
```

### Server Management
```bash
# Start server
python manage.py runserver

# Start on different port
python manage.py runserver 8080

# Start on all interfaces (accessible from network)
python manage.py runserver 0.0.0.0:8000

# Stop server
Ctrl+C
```

### Database Commands
```bash
# Create migrations (after model changes)
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# View migration status
python manage.py showmigrations

# Open database shell
python manage.py dbshell

# Create backup
pg_dump -U futur_user futurproctor_db > backup.sql
```

### User Management
```bash
# Create superuser (admin)
python manage.py createsuperuser

# Change password
python manage.py changepassword username
```

### Debugging Commands
```bash
# Django shell (interactive Python with Django loaded)
python manage.py shell

# Check for issues
python manage.py check

# View settings
python manage.py diffsettings

# Test email
python test_sendgrid.py
```

### Static Files
```bash
# Collect static files for production
python manage.py collectstatic

# Clear and recollect
python manage.py collectstatic --clear --no-input
```

---

## 🔧 .env File Template

**Location:** `/ProctoringME/futurproctor/.env`

```env
# Required - Database Configuration
DB_NAME=futurproctor_db
DB_USER=futur_user
DB_PASSWORD=12345678
DB_HOST=localhost
DB_PORT=5432

# Required - Django Settings
SECRET_KEY=django-insecure-z_+&zcw%md$8ai@dpaajebem^+#%_z)_32e%w-w3dz-j%xxrif
DEBUG=True

# Optional - Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Optional - AI Services
GROQ_API_KEY=your-groq-api-key
```

---

## 🌐 Important URLs

### Application URLs
| URL | Purpose | Login Required |
|-----|---------|----------------|
| http://127.0.0.1:8000/ | Homepage | No |
| http://127.0.0.1:8000/admin/ | Admin panel | Yes (superuser) |
| http://127.0.0.1:8000/register/ | User registration | No |
| http://127.0.0.1:8000/login/ | User login | No |

### External Resources
| Resource | URL | Purpose |
|----------|-----|---------|
| Demo Video | https://youtu.be/O8kfFmwkfOU | See app in action |
| Django Docs | https://docs.djangoproject.com/ | Framework reference |
| PostgreSQL Docs | https://www.postgresql.org/docs/ | Database reference |
| GROQ Console | https://console.groq.com/ | Get API key |

---

## 🐛 Quick Troubleshooting

| Problem | Quick Fix |
|---------|-----------|
| **Port already in use** | `python manage.py runserver 8080` |
| **Can't activate venv (Windows)** | `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser` |
| **Database connection failed** | Check PostgreSQL is running, verify .env credentials |
| **Module not found** | Ensure venv is activated, reinstall: `pip install -r ../requirements.txt` |
| **dlib installation failed** | Windows: `pip install dlib-19.22.99-cp310-cp310-win_amd64.whl` |
| **Static files not loading** | `python manage.py collectstatic` |
| **CSRF error** | Ensure `{% csrf_token %}` in forms |
| **Camera not working** | Grant browser permissions, close other apps using camera |

**For detailed solutions:** See [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

---

## 📦 Key Python Packages

| Package | Version | Purpose |
|---------|---------|---------|
| Django | 5.1.5 | Web framework |
| psycopg2-binary | 2.9.10 | PostgreSQL adapter |
| opencv-python | 4.11.0.86 | Computer vision |
| face-recognition | 1.3.0 | Face detection |
| ultralytics | 8.3.62 | YOLO object detection |
| torch | 2.5.1 | Deep learning |
| mediapipe | 0.10.18 | Face mesh & pose |
| groq | 0.4.2 | AI service client |
| python-dotenv | 1.0.0 | Load .env files |

---

## 🔐 Security Checklist

### Development ✅
- [x] DEBUG=True (shows errors)
- [x] Use provided SECRET_KEY
- [x] Simple passwords OK
- [x] ALLOWED_HOSTS=['*']
- [x] HTTP is fine

### Production ⚠️
- [ ] DEBUG=False (hide errors)
- [ ] Generate new SECRET_KEY
- [ ] Strong passwords (16+ chars)
- [ ] ALLOWED_HOSTS=['yourdomain.com']
- [ ] Use HTTPS/SSL
- [ ] Environment-specific .env
- [ ] Regular backups
- [ ] Firewall configured

---

## 🎓 Project Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    USER BROWSER                         │
│  (Camera, Microphone, Screen Monitoring)                │
└──────────────────┬──────────────────────────────────────┘
                   │ HTTP Requests
                   ▼
┌─────────────────────────────────────────────────────────┐
│                   DJANGO SERVER                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │              Views (views.py)                   │   │
│  │  • User authentication                          │   │
│  │  • Exam management                              │   │
│  │  • Proctoring logic                             │   │
│  └──────────┬──────────────────────────────────────┘   │
│             │                                           │
│  ┌──────────▼──────────────────────────────────────┐   │
│  │         Models (models.py)                      │   │
│  │  • User, Exam, Question                         │   │
│  │  • ViolationLog, ExamSession                    │   │
│  └──────────┬──────────────────────────────────────┘   │
│             │                                           │
└─────────────┼───────────────────────────────────────────┘
              │ Database Queries
              ▼
┌─────────────────────────────────────────────────────────┐
│               POSTGRESQL DATABASE                       │
│  • User data                                            │
│  • Exam data                                            │
│  • Proctoring logs                                      │
│  • Media files (images, videos)                         │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│                  AI/ML MODELS                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   YOLO v11   │  │    dlib      │  │  MediaPipe   │  │
│  │    Object    │  │     Face     │  │     Gaze     │  │
│  │  Detection   │  │  Detection   │  │   Tracking   │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│              EXTERNAL SERVICES                          │
│  • Email (SMTP)                                         │
│  • GROQ AI (Analysis)                                   │
│  • (Optional) Cloud Storage                             │
└─────────────────────────────────────────────────────────┘
```

---

## 💡 Pro Tips

### Daily Workflow
```bash
# Morning routine
cd ProctoringME/futurproctor
source venv/bin/activate
python manage.py runserver

# Evening routine
Ctrl+C  # Stop server
deactivate
```

### Making Changes
```bash
# After editing models.py
python manage.py makemigrations
python manage.py migrate

# After editing static files (CSS/JS)
Ctrl+Shift+R in browser  # Hard refresh

# After installing new packages
pip freeze > ../requirements.txt
```

### Testing
```bash
# Test single app
python manage.py test proctoring

# Test with verbosity
python manage.py test --verbosity=2

# Run specific test
python manage.py test proctoring.tests.TestClassName
```

---

## 📞 Need More Help?

| Guide | What It Covers | When to Use |
|-------|----------------|-------------|
| **EXECUTION_GUIDE.md** | Complete setup with explanations | First-time setup |
| **QUICK_START.md** | Fast 5-step setup | You know Django already |
| **PROJECT_STRUCTURE.md** | File and folder organization | Understanding codebase |
| **ENVIRONMENT_CONFIG.md** | .env file details | Configuration issues |
| **TROUBLESHOOTING.md** | Common problems & solutions | Something's broken |
| **README.md** | Project overview | Quick reference |
| **This file (CHEAT_SHEET.md)** | Quick commands & visuals | Daily reference |

---

## 🎯 Success Indicators

You know everything is working when:

✅ Terminal shows: `Starting development server at http://127.0.0.1:8000/`  
✅ Browser loads: Homepage without errors  
✅ Admin panel: http://127.0.0.1:8000/admin/ is accessible  
✅ Camera prompt: Browser asks for camera permission  
✅ Database: Can login with superuser credentials  
✅ No errors: Terminal shows clean request logs  

---

**🎉 Bookmark this file for quick reference while developing!**

**📚 Remember:** Detailed guides are available for every topic. This cheat sheet is just for quick lookups!
"