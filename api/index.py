import sys
import os

# Add the parent directory to path so we can import app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app

# Vercel expects a callable named 'app'
# Flask app object is already a WSGI callable
