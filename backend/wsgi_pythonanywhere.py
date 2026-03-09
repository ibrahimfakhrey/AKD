"""
PythonAnywhere WSGI Configuration Template for AKD
====================================================

DEPLOYMENT STEPS:
1. Upload project to PythonAnywhere via git clone or zip upload
2. Create a virtualenv:
      mkvirtualenv akd --python=/usr/bin/python3.10
3. Install dependencies:
      cd /home/USERNAME/AKD/backend && pip install -r requirements.txt
4. Create a new Web App → Manual Configuration → Python 3.10
5. Copy this file's contents into:
      /var/www/USERNAME_pythonanywhere_com_wsgi.py
6. In the Web tab, set virtualenv path:
      /home/USERNAME/.virtualenvs/akd
7. Create uploads directory:
      mkdir -p /home/USERNAME/AKD/backend/uploads
8. Seed the database (optional):
      cd /home/USERNAME/AKD/backend && python seed.py
9. Hit "Reload" on the Web tab

RESULT:
  https://USERNAME.pythonanywhere.com/         → User frontend
  https://USERNAME.pythonanywhere.com/admin/    → Admin panel
  https://USERNAME.pythonanywhere.com/api/v1/   → API
"""

import sys
import os

# ── EDIT THESE ──────────────────────────────────────────────
USERNAME = 'YOUR_PYTHONANYWHERE_USERNAME'         # <-- change this
PROJECT_DIR = f'/home/{USERNAME}/AKD/backend'
# ────────────────────────────────────────────────────────────

# Add project to path
sys.path.insert(0, PROJECT_DIR)

# Environment variables
os.environ['FLASK_CONFIG'] = 'pythonanywhere'
os.environ['SECRET_KEY'] = 'CHANGE-ME-to-a-random-string'          # <-- change this
os.environ['JWT_SECRET_KEY'] = 'CHANGE-ME-to-another-random-string' # <-- change this
os.environ['UPLOAD_FOLDER'] = os.path.join(PROJECT_DIR, 'uploads')

# Optional: use MySQL instead of SQLite
# os.environ['DATABASE_URL'] = 'mysql+pymysql://USERNAME:DB_PASSWORD@USERNAME.mysql.pythonanywhere-services.com/USERNAME$akd'

from app import create_app

application = create_app('pythonanywhere')
