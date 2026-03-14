"# ⚙️ Environment Configuration Guide

## Overview

The ProctoringME application uses a `.env` file to manage sensitive configuration and environment-specific settings. This keeps secrets out of the codebase and makes deployment easier.

## Creating the .env File

### Location
The `.env` file must be created in: `/ProctoringME/futurproctor/.env`

```
ProctoringME/
└── futurproctor/
    └── .env  ← Create here (same level as manage.py)
```

### Quick Create

#### Windows (Command Prompt):
```cmd
cd ProctoringME\futurproctor
type nul > .env
notepad .env
```

#### Windows (PowerShell):
```powershell
cd ProctoringME\futurproctor
New-Item .env -ItemType File
notepad .env
```

#### Linux/macOS:
```bash
cd ProctoringME/futurproctor
touch .env
nano .env  # or vim .env, or any text editor
```

---

## Complete .env Template

Copy this entire template into your `.env` file:

```env
# =============================================================================
# DJANGO CORE SETTINGS
# =============================================================================

# Secret key for Django - Keep this secret in production!
# Generate new one at: https://djecrety.ir/
SECRET_KEY=django-insecure-z_+&zcw%md$8ai@dpaajebem^+#%_z)_32e%w-w3dz-j%xxrif

# Debug mode - Set to False in production
# Values: True or False
DEBUG=True

# =============================================================================
# DATABASE CONFIGURATION (PostgreSQL)
# =============================================================================

# Database name
DB_NAME=futurproctor_db

# Database user
DB_USER=futur_user

# Database password
DB_PASSWORD=12345678

# Database host
# Use 'localhost' for local development
# Use IP/domain for remote database
DB_HOST=localhost

# Database port
# Default PostgreSQL port is 5432
DB_PORT=5432

# =============================================================================
# EMAIL CONFIGURATION (Optional)
# =============================================================================
# Required for sending email notifications, password resets, etc.

# Email backend - SMTP settings
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend

# SMTP server host
# Gmail: smtp.gmail.com
# Outlook: smtp-mail.outlook.com
# SendGrid: smtp.sendgrid.net
EMAIL_HOST=smtp.gmail.com

# SMTP port
# Gmail/Outlook TLS: 587
# Gmail/Outlook SSL: 465
EMAIL_PORT=587

# Use TLS encryption
EMAIL_USE_TLS=True

# Use SSL encryption (alternative to TLS)
EMAIL_USE_SSL=False

# Your email address
EMAIL_HOST_USER=your-email@gmail.com

# Email password or app password
# For Gmail, use App Password: https://myaccount.google.com/apppasswords
EMAIL_HOST_PASSWORD=your-app-specific-password

# Default 'from' email address
DEFAULT_FROM_EMAIL=your-email@gmail.com

# =============================================================================
# AI/ML SERVICE CONFIGURATION (Optional)
# =============================================================================

# GROQ API Key for AI-powered features
# Get your key at: https://console.groq.com/keys
GROQ_API_KEY=your-groq-api-key-here

# =============================================================================
# ADDITIONAL SETTINGS (Optional)
# =============================================================================

# Allowed hosts (comma-separated for production)
# Example: ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
# For development, this is set to * in settings.py
# ALLOWED_HOSTS=localhost,127.0.0.1

# Time zone
# TZ=UTC

# Language code
# LANGUAGE_CODE=en-us
```

---

## Configuration Sections Explained

### 1. Django Core Settings

#### SECRET_KEY
- **Purpose:** Cryptographic signing of sessions, cookies, password resets
- **Development:** Use the provided key
- **Production:** Generate a new secure key at https://djecrety.ir/
- **Important:** Never share this key publicly or commit to git!

#### DEBUG
- **Development:** Set to `True` (shows detailed error pages)
- **Production:** MUST set to `False` (hides sensitive error information)
- **Values:** `True` or `False` (case-sensitive)

### 2. Database Configuration

All database settings are **REQUIRED** and must match your PostgreSQL setup.

#### DB_NAME
- **Default:** `futurproctor_db`
- **Purpose:** Name of the PostgreSQL database
- **Must match:** The database you created in PostgreSQL

#### DB_USER
- **Default:** `futur_user`
- **Purpose:** PostgreSQL username
- **Must match:** The user you created in PostgreSQL

#### DB_PASSWORD
- **Default:** `12345678`
- **Purpose:** Password for the database user
- **Production:** Use a strong password (at least 16 characters, mix of letters, numbers, symbols)

#### DB_HOST
- **Development:** `localhost` or `127.0.0.1`
- **Production:** IP address or domain of your database server
- **Docker:** Use the service name (e.g., `postgres`)

#### DB_PORT
- **Default:** `5432` (standard PostgreSQL port)
- **Change only if:** Your PostgreSQL runs on a different port

### 3. Email Configuration (Optional)

Required only if your application sends emails (notifications, password resets, reports).

#### Gmail Setup Example

1. Enable 2-Factor Authentication on your Google account
2. Generate App Password:
   - Go to: https://myaccount.google.com/apppasswords
   - Select \"Mail\" and \"Other (Custom name)\"
   - Copy the 16-character password
3. Update `.env`:
```env
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=youremail@gmail.com
EMAIL_HOST_PASSWORD=your-16-char-app-password
```

#### SendGrid Setup Example

```env
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=your-sendgrid-api-key
```

### 4. AI/ML Services (Optional)

#### GROQ_API_KEY
- **Purpose:** AI-powered proctoring analysis features
- **Get Key:** https://console.groq.com/keys
- **Optional:** Application works without it, but AI features will be limited

---

## Examples for Different Scenarios

### Minimal Development Setup (Local PostgreSQL)

```env
SECRET_KEY=django-insecure-z_+&zcw%md$8ai@dpaajebem^+#%_z)_32e%w-w3dz-j%xxrif
DEBUG=True
DB_NAME=futurproctor_db
DB_USER=futur_user
DB_PASSWORD=12345678
DB_HOST=localhost
DB_PORT=5432
```

### Development with Email (Gmail)

```env
SECRET_KEY=django-insecure-z_+&zcw%md$8ai@dpaajebem^+#%_z)_32e%w-w3dz-j%xxrif
DEBUG=True
DB_NAME=futurproctor_db
DB_USER=futur_user
DB_PASSWORD=12345678
DB_HOST=localhost
DB_PORT=5432
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=myemail@gmail.com
EMAIL_HOST_PASSWORD=abcd efgh ijkl mnop
DEFAULT_FROM_EMAIL=myemail@gmail.com
```

### Production Setup

```env
SECRET_KEY=your-new-secure-generated-secret-key-here
DEBUG=False
DB_NAME=futurproctor_prod
DB_USER=futur_prod_user
DB_PASSWORD=SuperSecureP@ssw0rd!2024
DB_HOST=your-db-server.com
DB_PORT=5432
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=SG.your_sendgrid_api_key
GROQ_API_KEY=gsk_your_groq_api_key
```

### Docker Compose Setup

```env
SECRET_KEY=your-secret-key
DEBUG=True
DB_NAME=futurproctor_db
DB_USER=futur_user
DB_PASSWORD=12345678
DB_HOST=postgres  # Service name in docker-compose.yml
DB_PORT=5432
```

---

## Verification Steps

### 1. Check .env File Location
```bash
# From the futurproctor directory
ls -la .env
# Should show: .env file exists
```

### 2. Verify Django Reads .env
```bash
# Activate virtual environment first
python manage.py shell

# In Python shell:
>>> import os
>>> from dotenv import load_dotenv
>>> load_dotenv()
>>> print(os.environ.get('DB_NAME'))
# Should print: futurproctor_db

>>> print(os.environ.get('DEBUG'))
# Should print: True

>>> exit()
```

### 3. Test Database Connection
```bash
python manage.py dbshell
# Should connect to PostgreSQL
# Type \q to exit
```

### 4. Run Check Command
```bash
python manage.py check
# Should show: System check identified no issues (0 silenced).
```

---

## Common Issues & Solutions

### Issue 1: Settings Not Loading

**Symptom:** Django uses default values instead of .env values

**Causes:**
- `.env` file in wrong location
- `python-dotenv` not installed

**Solution:**
```bash
# Check file location
ls -la .env  # Should be in same folder as manage.py

# Install python-dotenv
pip install python-dotenv

# Verify settings.py has this at the top:
# from dotenv import load_dotenv
# load_dotenv()
```

### Issue 2: Database Connection Failed

**Symptom:** `django.db.utils.OperationalError: could not connect to server`

**Check:**
1. PostgreSQL is running
2. Database credentials in `.env` match PostgreSQL
3. Database and user exist in PostgreSQL

**Solution:**
```bash
# Test PostgreSQL connection manually
psql -U futur_user -d futurproctor_db -h localhost
# Enter password from .env
```

### Issue 3: Email Not Sending

**Symptom:** Email errors or emails not received

**For Gmail:**
- Enable 2FA
- Use App Password, not your regular password
- Allow less secure apps (if not using App Password)

**Test Email:**
```bash
python test_sendgrid.py
# Or use Django shell
python manage.py shell
>>> from django.core.mail import send_mail
>>> send_mail('Test', 'Body', 'from@example.com', ['to@example.com'])
```

### Issue 4: SECRET_KEY Error

**Symptom:** `django.core.exceptions.ImproperlyConfigured: The SECRET_KEY setting must not be empty.`

**Solution:**
- Verify `.env` file exists
- Check `SECRET_KEY=` line has a value (no spaces around =)
- Restart the Django server after creating .env

---

## Security Best Practices

### ✅ DO:
- Keep `.env` file out of version control (add to .gitignore)
- Use strong passwords in production
- Generate a new SECRET_KEY for production
- Set DEBUG=False in production
- Use environment-specific .env files (.env.dev, .env.prod)
- Regularly rotate API keys and passwords
- Use HTTPS in production

### ❌ DON'T:
- Commit `.env` to git
- Share your `.env` file
- Use default passwords in production
- Leave DEBUG=True in production
- Hardcode secrets in code
- Use the same SECRET_KEY across environments

---

## Environment Variable Loading Order

Django loads settings in this order (last one wins):

1. `settings.py` default values
2. `.env` file (via load_dotenv())
3. System environment variables
4. Command-line environment variables

Example:
```bash
# .env file has DB_NAME=futurproctor_db
# Override temporarily:
DB_NAME=test_db python manage.py runserver
```

---

## Useful Commands

### View Current Environment Variables
```bash
# Linux/macOS
env | grep DB_

# Windows PowerShell
gci env: | Where-Object {$_.Name -like \"DB_*\"}
```

### Copy .env Template
```bash
# Create a template file others can use
cp .env .env.example
# Edit .env.example and replace sensitive values with placeholders
```

### Backup .env
```bash
cp .env .env.backup
```

---

## Quick Reference

| Variable | Required | Default | Purpose |
|----------|----------|---------|---------|
| SECRET_KEY | Yes | (provided) | Django security |
| DEBUG | Yes | True | Show errors |
| DB_NAME | Yes | futurproctor_db | Database name |
| DB_USER | Yes | futur_user | DB username |
| DB_PASSWORD | Yes | 12345678 | DB password |
| DB_HOST | Yes | localhost | DB server |
| DB_PORT | Yes | 5432 | DB port |
| EMAIL_HOST | No | - | SMTP server |
| EMAIL_PORT | No | 587 | SMTP port |
| EMAIL_USE_TLS | No | True | Use TLS |
| EMAIL_HOST_USER | No | - | Email address |
| EMAIL_HOST_PASSWORD | No | - | Email password |
| GROQ_API_KEY | No | - | AI service key |

---

**Remember:** After making changes to `.env`, you must restart the Django development server for changes to take effect!

```bash
# Stop server: Ctrl+C
# Start again: python manage.py runserver
```
"