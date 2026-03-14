"# 🔐 Credentials Setup Guide - ProctoringME

## Overview

This guide will walk you through setting up all required credentials and API keys for the ProctoringME application. Each section provides step-by-step instructions to obtain and configure the necessary credentials.

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Django Configuration](#django-configuration)
3. [Database Setup](#database-setup)
4. [GROQ API Setup](#groq-api-setup)
5. [SendGrid Email Setup](#sendgrid-email-setup)
6. [Complete .env File](#complete-env-file)
7. [Verification & Testing](#verification--testing)
8. [Security Best Practices](#security-best-practices)

---

## Prerequisites

Before you begin, ensure you have:
- [ ] Python 3.10.0 installed
- [ ] Git installed
- [ ] A text editor (VS Code, Sublime, Notepad++, etc.)
- [ ] Email account for SendGrid registration
- [ ] Internet connection for API key generation

---

## Django Configuration

### 1. SECRET_KEY

**Purpose:** Used by Django for cryptographic signing (sessions, cookies, password resets)

**For Development:**
```env
SECRET_KEY=django-insecure-z_+&zcw%md$8ai@dpaajebem^+#%_z)_32e%w-w3dz-j%xxrif
```

**For Production - Generate New Key:**

**Option 1: Using Python**
```bash
python -c \"from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())\"
```

**Option 2: Using Online Generator**
Visit: https://djecrety.ir/

**Option 3: Using Django Shell**
```bash
python manage.py shell
>>> from django.core.management.utils import get_random_secret_key
>>> print(get_random_secret_key())
>>> exit()
```

⚠️ **Important:** Never use the same SECRET_KEY in production that's shown in public repositories!

---

### 2. DEBUG

**Purpose:** Controls debug mode in Django

```env
DEBUG=True    # Development - Shows detailed error pages
DEBUG=False   # Production - Hides sensitive error information
```

**Development:** Set to `True`  
**Production:** Must be set to `False`

---

### 3. ALLOWED_HOSTS

**Purpose:** List of host/domain names that Django can serve

**Development:**
```env
ALLOWED_HOSTS=127.0.0.1,localhost
```

**Production:**
```env
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,your-ip-address
```

**Note:** No spaces between comma-separated values!

---

## Database Setup

You have two options for database configuration:

### Option 1: DATABASE_URL (Recommended for Cloud Databases)

**Format:**
```env
DATABASE_URL=postgresql://username:password@host:port/database_name
```

**Your Configuration:**
```env
DATABASE_URL=postgresql://futur_user:d9M1xX0Po9yh11Ku0Fg5f8CO9FTqP84H@dpg-d6imv524d50c7384p25g-a/futurproctor_db
```

**Breaking Down the URL:**
- **Protocol:** `postgresql://`
- **Username:** `futur_user`
- **Password:** `d9M1xX0Po9yh11Ku0Fg5f8CO9FTqP84H`
- **Host:** `dpg-d6imv524d50c7384p25g-a`
- **Database Name:** `futurproctor_db`

This appears to be a **Render.com** or similar cloud PostgreSQL database.

---

### Option 2: Individual Database Variables (For Local PostgreSQL)

```env
DB_NAME=futurproctor_db
DB_USER=futur_user
DB_PASSWORD=12345678
DB_HOST=localhost
DB_PORT=5432
```

---

### Setting Up Local PostgreSQL Database

If you're using local PostgreSQL, follow these steps:

#### Step 1: Install PostgreSQL

**Windows:**
- Download from: https://www.postgresql.org/download/windows/
- Run installer, remember the password you set

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

**macOS:**
```bash
brew install postgresql
brew services start postgresql
```

#### Step 2: Create Database and User

**Login to PostgreSQL:**
```bash
# Linux/macOS
sudo -u postgres psql

# Windows - Use SQL Shell (psql) from Start Menu
```

**Run These SQL Commands:**
```sql
-- Create the database
CREATE DATABASE futurproctor_db;

-- Create the user with password
CREATE USER futur_user WITH PASSWORD '12345678';

-- Grant privileges to the user
ALTER ROLE futur_user SET client_encoding TO 'utf8';
ALTER ROLE futur_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE futur_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE futurproctor_db TO futur_user;

-- For PostgreSQL 15+ (additional permission)
\c futurproctor_db
GRANT ALL ON SCHEMA public TO futur_user;

-- Exit
\q
```

#### Step 3: Verify Connection

```bash
# Test connection
psql -U futur_user -d futurproctor_db -h localhost

# Enter password: 12345678
# If successful, you'll see the PostgreSQL prompt
# Type \q to exit
```

#### Step 4: Update .env File

**For Local Database:**
```env
DB_NAME=futurproctor_db
DB_USER=futur_user
DB_PASSWORD=12345678
DB_HOST=localhost
DB_PORT=5432
```

**For Cloud Database (Render, Railway, etc.):**
```env
DATABASE_URL=postgresql://futur_user:d9M1xX0Po9yh11Ku0Fg5f8CO9FTqP84H@dpg-d6imv524d50c7384p25g-a/futurproctor_db
```

---

## GROQ API Setup

**Purpose:** AI-powered analysis for proctoring features (suspicious behavior detection, audio analysis)

### Step 1: Create GROQ Account

1. Visit: https://console.groq.com/
2. Click **\"Sign Up\"** or **\"Get Started\"**
3. Sign up with:
   - Google account
   - GitHub account
   - Email & password

### Step 2: Generate API Key

1. After login, navigate to **API Keys** section
2. Click **\"Create API Key\"**
3. Give it a name: `ProctoringME` or `Development`
4. Click **\"Create\"**
5. **Copy the API key immediately** (you won't see it again!)

**Example API Key Format:**
```
gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### Step 3: Add to .env File

```env
GROQ_API_KEY=groq-api-key
```

### Step 4: Test GROQ Connection

```bash
# Activate virtual environment first
source venv/bin/activate  # Linux/macOS
# OR
venv\Scripts\activate     # Windows

# Test GROQ service
python manage.py shell
```

```python
from groq import Groq
import os

client = Groq(api_key=os.environ.get('GROQ_API_KEY'))
completion = client.chat.completions.create(
    model=\"mixtral-8x7b-32768\",
    messages=[{\"role\": \"user\", \"content\": \"Hello!\"}]
)
print(completion.choices[0].message.content)
```

If successful, you'll see a response from GROQ!

**Available Models:**
- `mixtral-8x7b-32768` - Fast, general purpose
- `llama2-70b-4096` - Large model
- `gemma-7b-it` - Lightweight

---

## SendGrid Email Setup

**Purpose:** Send emails for notifications, password resets, exam reports

### Step 1: Create SendGrid Account

1. Visit: https://signup.sendgrid.com/
2. Click **\"Create Account\"**
3. Fill in details:
   - Email address
   - Password
   - First & Last name
4. Verify your email address

### Step 2: Complete Sender Authentication

SendGrid requires you to verify your sender identity:

**Option A: Single Sender Verification (Easiest for Development)**

1. Go to: **Settings → Sender Authentication**
2. Click **\"Verify a Single Sender\"**
3. Fill in your details:
   - **From Name:** Your name or app name
   - **From Email:** `vikrantsingh.it2023@nsec.ac.in` (your email)
   - **Reply To:** Same email
   - **Address, City, State, etc.** (required by law)
4. Click **\"Create\"**
5. Check your email and click the verification link

**Option B: Domain Authentication (For Production)**

1. Go to: **Settings → Sender Authentication**
2. Click **\"Authenticate Your Domain\"**
3. Follow DNS setup instructions (requires domain access)

### Step 3: Generate API Key

1. Go to: **Settings → API Keys**
2. Click **\"Create API Key\"**
3. **Name:** `ProctoringME` or `Development`
4. **Permissions:** Select **\"Full Access\"** (for development)
   - For production, use **\"Restricted Access\"** with only Mail Send permission
5. Click **\"Create & View\"**
6. **Copy the API key immediately!** (starts with `SG.`)

**API Key Format:**
```
SG.xxxxxxxxxxxxxxxxxxxxxxx.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### Step 4: Add to .env File

```env
# SendGrid Configuration
SENDGRID_API_KEY=sendgrid-api-key
DEFAULT_FROM_EMAIL=vikrantsingh.it2023@nsec.ac.in
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=apikey
```

**Important Notes:**
- `DEFAULT_FROM_EMAIL` must be verified in SendGrid (Step 2)
- `EMAIL_HOST_USER` is always `apikey` (literally the word \"apikey\")
- `SENDGRID_API_KEY` is your actual API key

### Step 5: Test SendGrid Email

**Method 1: Using Test Script**
```bash
# Make sure you're in futurproctor directory
python test_sendgrid.py
```

**Method 2: Using Django Shell**
```bash
python manage.py shell
```

```python
from django.core.mail import send_mail
from django.conf import settings

send_mail(
    'Test Email from ProctoringME',
    'This is a test email to verify SendGrid configuration.',
    settings.DEFAULT_FROM_EMAIL,
    ['your-test-email@example.com'],
    fail_silently=False,
)
```

**Expected Result:** You should receive the test email within a few seconds!

### Step 6: Troubleshooting SendGrid

**Issue: \"The from address does not match a verified Sender Identity\"**

**Solution:** 
- Verify your sender email in SendGrid (Step 2 above)
- Ensure `DEFAULT_FROM_EMAIL` matches the verified email exactly

**Issue: \"403 Forbidden\"**

**Solution:**
- Check API key has correct permissions
- Regenerate API key with Full Access
- Ensure no extra spaces in .env file

**Issue: Emails not arriving**

**Solutions:**
1. Check spam/junk folder
2. Try sending to different email provider (Gmail, Outlook)
3. Check SendGrid dashboard for delivery status: **Activity → Email Activity**
4. Verify sender authentication is complete

---

## Complete .env File

### Location

Create this file at: `/ProctoringME/futurproctor/.env`

```
ProctoringME/
└── futurproctor/
    └── .env  ← Create here
```

### Full Template

Copy this entire template and fill in your actual values:

```env
# =============================================================================
# DJANGO CORE SETTINGS
# =============================================================================

# Secret key for Django cryptographic signing
SECRET_KEY=django-insecure-z_+&zcw%md$8ai@dpaajebem^+#%_z)_32e%w-w3dz-j%xxrif

# Debug mode (True for development, False for production)
DEBUG=True

# Allowed hosts (comma-separated, no spaces)
ALLOWED_HOSTS=127.0.0.1,localhost

# =============================================================================
# DATABASE CONFIGURATION
# =============================================================================

# Option 1: Database URL (for cloud databases like Render, Railway)
DATABASE_URL=postgresql://futur_user:d9M1xX0Po9yh11Ku0Fg5f8CO9FTqP84H@dpg-d6imv524d50c7384p25g-a/futurproctor_db

# Option 2: Individual database variables (for local PostgreSQL)
DB_NAME=futurproctor_db
DB_USER=futur_user
DB_PASSWORD=12345678
DB_HOST=localhost
DB_PORT=5432

# =============================================================================
# GROQ API CONFIGURATION
# =============================================================================

# GROQ API key for AI-powered proctoring analysis
# Get your key at: https://console.groq.com/keys
GROQ_API_KEY=groq-api-key

# =============================================================================
# SENDGRID EMAIL CONFIGURATION
# =============================================================================

# SendGrid API key for sending emails
# Get your key at: https://app.sendgrid.com/settings/api_keys
SENDGRID_API_KEY=sendgrid-api-key

# Email configuration
DEFAULT_FROM_EMAIL=vikrantsingh.it2023@nsec.ac.in
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=apikey

# =============================================================================
# PYTHON VERSION
# =============================================================================

# Python version (for deployment platforms)
PYTHON_VERSION=3.10.0
```

---

## Verification & Testing

### Step 1: Verify .env File Exists

```bash
# Navigate to futurproctor directory
cd ProctoringME/futurproctor

# Check if .env file exists
ls -la .env  # Linux/macOS
dir .env     # Windows
```

### Step 2: Test Environment Variables Loading

```bash
# Activate virtual environment
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# Start Django shell
python manage.py shell
```

```python
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Test each variable
print("SECRET_KEY:", os.environ.get('SECRET_KEY')[:20] + "...")
print("DEBUG:", os.environ.get('DEBUG'))
print("DB_NAME:", os.environ.get('DB_NAME'))
print("DB_USER:", os.environ.get('DB_USER'))
print("GROQ_API_KEY:", os.environ.get('GROQ_API_KEY')[:10] + "...")
print("SENDGRID_API_KEY:", os.environ.get('SENDGRID_API_KEY')[:10] + "...")
print("DEFAULT_FROM_EMAIL:", os.environ.get('DEFAULT_FROM_EMAIL'))

# Exit
exit()
```

**Expected Output:**
```
SECRET_KEY: django-insecure-z_+&...
DEBUG: True
DB_NAME: futurproctor_db
DB_USER: futur_user
GROQ_API_KEY: gsk_ahh5ba...
SENDGRID_API_KEY: SG.acQQn1t...
DEFAULT_FROM_EMAIL: vikrantsingh.it2023@nsec.ac.in
```

### Step 3: Test Database Connection

```bash
# Test database connection
python manage.py dbshell
```

If successful, you'll enter PostgreSQL prompt. Type `q` to exit.

**If connection fails:**
- Verify PostgreSQL is running
- Check credentials in .env match your database
- For cloud databases, ensure your IP is whitelisted

### Step 4: Run Django Checks

```bash
# Run system checks
python manage.py check

# Expected output:
# System check identified no issues (0 silenced).
```

### Step 5: Apply Migrations

```bash
# Create and apply migrations
python manage.py makemigrations
python manage.py migrate
```

**Expected Output:**
```
Operations to perform:
  Apply all migrations: admin, auth, contenttypes, proctoring, sessions
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
  ...
```

### Step 6: Test GROQ API

```bash
# Run the test (if available)
python manage.py shell
```

```python
from proctoring.groq_service import test_groq
test_groq()
```

### Step 7: Test SendGrid Email

```bash
# Run SendGrid test
python test_sendgrid.py
```

**Check:**
- Terminal shows "Email sent successfully!"
- Email arrives in your inbox (check spam folder too)

---

## Security Best Practices

### 🔒 For Development

✅ **DO:**
- Use the provided credentials for testing
- Keep .env file in .gitignore
- Use DEBUG=True to see errors
- Test all services before building features

❌ **DON'T:**
- Commit .env file to git
- Share .env file publicly
- Use production credentials in development

### 🔐 For Production

✅ **DO:**
- Generate new SECRET_KEY
- Set DEBUG=False
- Use strong database passwords
- Rotate API keys regularly
- Use environment-specific .env files
- Enable 2FA on all service accounts
- Monitor API usage and billing
- Set up proper ALLOWED_HOSTS
- Use HTTPS/SSL
- Restrict SendGrid API key permissions

❌ **DON'T:**
- Use default/example credentials
- Leave DEBUG=True
- Expose .env file
- Share API keys
- Use weak passwords
- Ignore security warnings

---

## Common Issues & Solutions

### Issue 1: .env File Not Loading

**Symptom:** Django uses default values, ignoring .env

**Solutions:**
```bash
# 1. Verify file location
pwd  # Should be in futurproctor directory
ls .env  # File should exist

# 2. Check python-dotenv is installed
pip list | grep dotenv

# 3. If not installed:
pip install python-dotenv

# 4. Verify settings.py loads .env
# Should have at the top:
# from dotenv import load_dotenv
# load_dotenv()
```

### Issue 2: Database Connection Failed

**Error:** `django.db.utils.OperationalError: could not connect to server`

**Solutions:**

**For Local Database:**
```bash
# Check PostgreSQL is running
sudo systemctl status postgresql  # Linux
# Windows: Check Services for postgresql

# Test connection manually
psql -U futur_user -d futurproctor_db -h localhost

# If fails, recreate user/database (see Database Setup section)
```

**For Cloud Database:**
```bash
# Verify DATABASE_URL is correct
# Check if your IP is whitelisted on the cloud provider
# Test connection string with psql:
psql postgresql://futur_user:password@host/database
```

### Issue 3: GROQ API Error

**Error:** `401 Unauthorized` or `403 Forbidden`

**Solutions:**
1. Verify API key is correct (no extra spaces)
2. Check account has credits/is active
3. Regenerate API key in GROQ console
4. Update .env with new key
5. Restart Django server

### Issue 4: SendGrid Email Not Sending

**Error:** `The from address does not match a verified Sender Identity`

**Solutions:**
1. Verify sender email in SendGrid dashboard
2. Wait for verification email and click link
3. Ensure DEFAULT_FROM_EMAIL matches verified email exactly
4. Check sender verification status: Settings → Sender Authentication

**Error:** `403 Forbidden`

**Solutions:**
1. Regenerate API key with correct permissions
2. Ensure API key has Mail Send permission
3. Check account is not suspended
4. Verify no typos in API key

### Issue 5: Python Version Mismatch

**Symptom:** Errors during pip install

**Solutions:**
```bash
# Check Python version
python --version

# Should be 3.10.x
# If not, install Python 3.10:
# - Windows: python.org
# - Linux: sudo apt install python3.10
# - macOS: brew install python@3.10
```

---

## Quick Reference Card

### Where to Get Credentials

| Service | Where to Get | URL |
|---------|--------------|-----|
| **Django SECRET_KEY** | Generate with Python | `python -c \"from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())\"` |
| **Database** | PostgreSQL installation | Local: `localhost:5432` |
| **GROQ API** | GROQ Console | https://console.groq.com/keys |
| **SendGrid** | SendGrid Dashboard | https://app.sendgrid.com/settings/api_keys |

### Testing Commands

```bash
# Test database
python manage.py dbshell

# Test Django setup
python manage.py check

# Test email
python test_sendgrid.py

# Test GROQ (in Django shell)
from proctoring.groq_service import test_groq
test_groq()
```

---

## Final Checklist

Before running the application, ensure:

- [ ] .env file created in `/ProctoringME/futurproctor/.env`
- [ ] All credentials added to .env file
- [ ] PostgreSQL database created and accessible
- [ ] GROQ API key generated and tested
- [ ] SendGrid sender email verified
- [ ] SendGrid API key generated and tested
- [ ] python-dotenv installed
- [ ] Virtual environment activated
- [ ] No syntax errors in .env file (no extra spaces, quotes)
- [ ] Migrations applied successfully
- [ ] Django checks pass with no issues

---

## Next Steps

After setting up all credentials:

1. ✅ Run migrations: `python manage.py migrate`
2. ✅ Create superuser: `python manage.py createsuperuser`
3. ✅ Start server: `python manage.py runserver`
4. ✅ Access application: http://127.0.0.1:8000/
5. ✅ Test all features

---

## Support Resources

- **Django Settings Docs:** https://docs.djangoproject.com/en/5.1/ref/settings/
- **PostgreSQL Docs:** https://www.postgresql.org/docs/
- **GROQ Documentation:** https://console.groq.com/docs
- **SendGrid Documentation:** https://docs.sendgrid.com/
- **Project Troubleshooting:** See TROUBLESHOOTING.md

---

**🎉 Congratulations! Your credentials are now configured. You're ready to run the ProctoringME application!**

For complete setup instructions, see [EXECUTION_GUIDE.md](EXECUTION_GUIDE.md)
"