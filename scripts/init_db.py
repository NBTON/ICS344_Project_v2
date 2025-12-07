import sys
import os

# Add the root directory to python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app import create_app
from backend.database import db

app = create_app()

with app.app_context():
    db.create_all()
    print("Database initialized successfully.")
