"# 🚀 ProctoringME - Complete Execution Guide

## 📋 Table of Contents
1. [Prerequisites](#prerequisites)
2. [System Requirements](#system-requirements)
3. [Installation Steps](#installation-steps)
4. [Database Setup](#database-setup)
5. [Environment Configuration](#environment-configuration)
6. [Running the Application](#running-the-application)
7. [Testing the Application](#testing-the-application)
8. [Troubleshooting](#troubleshooting)
9. [Common Issues & Solutions](#common-issues--solutions)

---

## Prerequisites

Before starting, ensure you have the following installed on your system:

### Required Software:
- **Python 3.10** (Recommended - compatible with the project dependencies)
- **PostgreSQL 12+** (Database)
- **pip** (Python package manager)
- **Git** (For cloning the repository)

### Check Installed Versions:
```bash
python --version    # Should show Python 3.10.x
pip --version
psql --version      # PostgreSQL version
git --version
```

---

## System Requirements

- **Operating System**: Windows 10/11, Linux (Ubuntu 20.04+), or macOS
- **RAM**: Minimum 4GB (8GB recommended for AI models)
- **Storage**: At least 2GB free space
- **Internet Connection**: Required for initial setup and dependency installation

---

## Installation Steps

### Step 1: Clone the Repository

Open your terminal/command prompt and run:

```bash
# Clone the repository
git clone https://github.com/vikrantan5/ProctoringME.git

# Navigate to the project directory
cd ProctoringME
```

### Step 2: Navigate to the Django Project Folder

```bash
# Go into the main Django project folder
cd futurproctor
```

**Important Note:** All subsequent commands should be run from the `futurproctor` directory unless otherwise specified.

### Step 3: Create Virtual Environment

Creating a virtual environment isolates your project dependencies from other Python projects.

#### On Windows:
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate
```

#### On Linux/macOS:
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate
```

**You should see `(venv)` prefix in your terminal, indicating the virtual environment is active.**

### Step 4: Upgrade pip

```bash
# Upgrade pip to the latest version
python -m pip install --upgrade pip
```

### Step 5: Install Python Dependencies

This step will install all required packages including Django, AI/ML libraries, and database drivers.

```bash
# Install all dependencies from requirements.txt
pip install -r ../requirements.txt
```

**Note:** This may take 10-15 minutes depending on your internet speed as it includes heavy libraries like:
- TensorFlow/PyTorch
- OpenCV
- MediaPipe
- dlib
- face_recognition
- ultralytics (YOLO)

**Special Note for Windows Users:**
If you encounter errors with `dlib` installation, the project includes a pre-built wheel file. Install it manually:

```bash
pip install dlib-19.22.99-cp310-cp310-win_amd64.whl
```

---

## Database Setup

### Step 1: Install PostgreSQL

If PostgreSQL is not installed:

#### Windows:
- Download from: https://www.postgresql.org/download/windows/
- Run the installer and follow the setup wizard
- Remember the password you set for the `postgres` user

#### Linux (Ubuntu/Debian):
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

#### macOS:
```bash
brew install postgresql
brew services start postgresql
```

### Step 2: Create Database and User

Open PostgreSQL command line:

#### Windows:
Search for \"SQL Shell (psql)\" in Start Menu and open it.

#### Linux/macOS:
```bash
sudo -u postgres psql
```

Then run these SQL commands:

```sql
-- Create database
CREATE DATABASE futurproctor_db;

-- Create user
CREATE USER futur_user WITH PASSWORD '12345678';

-- Grant privileges
ALTER ROLE futur_user SET client_encoding TO 'utf8';
ALTER ROLE futur_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE futur_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE futurproctor_db TO futur_user;

-- Exit PostgreSQL
\q
```

**Important:** You can change the database name, username, and password, but you'll need to update them in the `.env` file (next step).

---

## Environment Configuration

### Step 1: Create `.env` File

The application uses environment variables for sensitive configuration. Create a `.env` file in the `futurproctor` directory:

```bash
# Make sure you're in the futurproctor directory
# Create .env file (Windows - use notepad, Linux/macOS - use nano/vim)
```

#### On Windows:
```bash
type nul > .env
notepad .env
```

#### On Linux/macOS:
```bash
touch .env
nano .env
```

### Step 2: Add Environment Variables

Copy and paste the following into your `.env` file:

```env
# Django Settings
SECRET_KEY=django-insecure-z_+&zcw%md$8ai@dpaajebem^+#%_z)_32e%w-w3dz-j%xxrif
DEBUG=True

# Database Configuration
DB_NAME=futurproctor_db
DB_USER=futur_user
DB_PASSWORD=12345678
DB_HOST=localhost
DB_PORT=5432

# Email Configuration (Optional - for email features)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# GROQ API Configuration (Optional - for AI features)
GROQ_API_KEY=your-groq-api-key-here
```

**Important Notes:**
- If you used different database credentials in Step 2 of Database Setup, update them here
- Email and GROQ API keys are optional for basic functionality
- Save and close the file

---

## Running the Application

### Step 1: Apply Database Migrations

Migrations create the necessary database tables for the application.

```bash
# Make sure you're in the futurproctor directory and venv is activated
python manage.py makemigrations
python manage.py migrate
```

**Expected Output:** You should see messages like \"Applying proctoring.0001_initial... OK\"

### Step 2: Create Superuser (Admin Account)

Create an admin account to access the Django admin panel:

```bash
python manage.py createsuperuser
```

**You'll be prompted to enter:**
- Username (e.g., admin)
- Email address (can be fake for development)
- Password (enter twice)

### Step 3: Collect Static Files (Optional for Development)

```bash
python manage.py collectstatic --no-input
```

### Step 4: Start the Development Server

```bash
python manage.py runserver
```

**Expected Output:**
```
Watching for file changes with StatReloader
Performing system checks...

System check identified no issues (0 silenced).
March 08, 2025 - 15:30:00
Django version 5.1.5, using settings 'futurproctor.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
```

---

## Testing the Application

### Step 1: Access the Application

Open your web browser and navigate to:

**Main Application:**
```
http://127.0.0.1:8000/
```

**Admin Panel:**
```
http://127.0.0.1:8000/admin/
```
- Login with the superuser credentials you created

### Step 2: Test Basic Functionality

1. **Homepage:** Should load with login/register options
2. **Admin Panel:** Login and verify database connections
3. **User Registration:** Try creating a test student account
4. **Camera Access:** Grant camera permissions when prompted (required for face detection)
5. **Exam Interface:** Navigate through the exam flow

---

## Troubleshooting

### Verify Your Setup

If you encounter issues, verify each step:

```bash
# 1. Check if virtual environment is activated
# Your terminal should show (venv) prefix

# 2. Check Python version
python --version  # Should be 3.10.x

# 3. Verify Django installation
python -m django --version  # Should show 5.1.5

# 4. Check database connection
python manage.py dbshell  # Should connect to PostgreSQL
# Type \q to exit

# 5. Check if migrations are applied
python manage.py showmigrations
```

---

## Common Issues & Solutions

### 1. **Port Already in Use**

**Error:** `Error: That port is already in use.`

**Solution:** Either kill the process using port 8000 or run on a different port:
```bash
python manage.py runserver 8080
```
Then access: http://127.0.0.1:8080/

### 2. **Database Connection Error**

**Error:** `django.db.utils.OperationalError: could not connect to server`

**Solutions:**
- Verify PostgreSQL is running:
  ```bash
  # Windows: Check Services
  # Linux: sudo systemctl status postgresql
  ```
- Check database credentials in `.env` file
- Verify database and user exist in PostgreSQL

### 3. **Module Not Found Errors**

**Error:** `ModuleNotFoundError: No module named 'xyz'`

**Solution:**
```bash
# Make sure virtual environment is activated
# Reinstall dependencies
pip install -r ../requirements.txt
```

### 4. **dlib Installation Failed**

**Error during pip install:** `ERROR: Failed building wheel for dlib`

**Solution for Windows:**
```bash
# Use the provided wheel file
pip install dlib-19.22.99-cp310-cp310-win_amd64.whl
```

**Solution for Linux/macOS:**
```bash
# Install build tools first
sudo apt-get install build-essential cmake  # Ubuntu/Debian
# OR
brew install cmake  # macOS

# Then install dlib
pip install dlib
```

### 5. **Camera/Webcam Not Working**

**Issue:** Face detection not working

**Solutions:**
- Grant browser camera permissions
- Check if camera is being used by another application
- For Linux, you may need to add your user to the video group:
  ```bash
  sudo usermod -a -G video $USER
  ```

### 6. **Static Files Not Loading**

**Issue:** CSS/JavaScript not loading correctly

**Solution:**
```bash
python manage.py collectstatic --clear --no-input
```

### 7. **Virtual Environment Not Activating**

**Windows PowerShell Error:** `cannot be loaded because running scripts is disabled`

**Solution:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 8. **YOLO Model Not Found**

**Error:** Model file `yolo11s.pt` not found

**Solution:** Ensure you're running commands from the `futurproctor` directory where `yolo11s.pt` is located.

---

## Quick Start Checklist

- [ ] Python 3.10 installed
- [ ] PostgreSQL installed and running
- [ ] Repository cloned
- [ ] Navigated to `futurproctor` directory
- [ ] Virtual environment created and activated
- [ ] Dependencies installed from requirements.txt
- [ ] Database created (futurproctor_db)
- [ ] Database user created (futur_user)
- [ ] `.env` file created with correct credentials
- [ ] Migrations applied (`python manage.py migrate`)
- [ ] Superuser created (`python manage.py createsuperuser`)
- [ ] Server running (`python manage.py runserver`)
- [ ] Application accessible at http://127.0.0.1:8000/

---

## Additional Commands

### Stop the Server
Press `CTRL+C` in the terminal where the server is running

### Deactivate Virtual Environment
```bash
deactivate
```

### Restart Everything
```bash
# Activate virtual environment
source venv/bin/activate  # Linux/macOS
# OR
venv\Scripts\activate  # Windows

# Start server
python manage.py runserver
```

### View Logs
Check terminal output where `runserver` is running for real-time logs

---

## Next Steps

After successful setup:
1. Explore the admin panel to manage exams, students, and questions
2. Test the proctoring features with a webcam
3. Review the AI model configurations in the code
4. Customize the application as needed

---

## Support & Resources

- **Project Demo:** https://youtu.be/O8kfFmwkfOU
- **Django Documentation:** https://docs.djangoproject.com/
- **PostgreSQL Documentation:** https://www.postgresql.org/docs/

---

## Security Notes

⚠️ **Important for Production:**
- Change the `SECRET_KEY` in `.env` to a secure random string
- Set `DEBUG=False` in production
- Use strong database passwords
- Configure allowed hosts properly
- Set up HTTPS/SSL
- Never commit `.env` file to version control

---

**Congratulations! Your ProctoringME application should now be running successfully! 🎉**

If you encounter any issues not covered in this guide, please check the terminal output for specific error messages and refer to the troubleshooting section.
"