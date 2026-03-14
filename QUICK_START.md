"# ⚡ Quick Start Guide - ProctoringME

This is a condensed version for experienced developers. For detailed instructions, see [EXECUTION_GUIDE.md](EXECUTION_GUIDE.md).

## Prerequisites
- Python 3.10
- PostgreSQL 12+
- Git

## Quick Setup (5 Steps)

### 1. Clone & Navigate
```bash
git clone https://github.com/vikrantan5/ProctoringME.git
cd ProctoringME/futurproctor
```

### 2. Setup Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install --upgrade pip
pip install -r ../requirements.txt
```

### 4. Setup Database
```bash
# Login to PostgreSQL
sudo -u postgres psql  # Linux/macOS
# OR use SQL Shell on Windows

# Run these SQL commands:
CREATE DATABASE futurproctor_db;
CREATE USER futur_user WITH PASSWORD '12345678';
GRANT ALL PRIVILEGES ON DATABASE futurproctor_db TO futur_user;
\q
```

### 5. Configure & Run
```bash
# Create .env file
cat > .env << EOL
SECRET_KEY=django-insecure-z_+&zcw%md\$8ai@dpaajebem^+#%_z)_32e%w-w3dz-j%xxrif
DEBUG=True
DB_NAME=futurproctor_db
DB_USER=futur_user
DB_PASSWORD=12345678
DB_HOST=localhost
DB_PORT=5432
EOL

# Apply migrations
python manage.py migrate

# Create admin user
python manage.py createsuperuser

# Run server
python manage.py runserver
```

## Access Application
- **Main App:** http://127.0.0.1:8000/
- **Admin Panel:** http://127.0.0.1:8000/admin/

## Common Commands
```bash
# Activate venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# Run server
python manage.py runserver

# Stop server
CTRL+C

# Deactivate venv
deactivate
```

## Troubleshooting
See [EXECUTION_GUIDE.md](EXECUTION_GUIDE.md) for detailed troubleshooting.

**Quick Fixes:**
- Port in use: `python manage.py runserver 8080`
- DB error: Check PostgreSQL is running & credentials in `.env`
- Module error: Reinstall dependencies `pip install -r ../requirements.txt`
"