import sys
import os
import traceback
from flask import Flask

# Add the parent directory to path so we can import the real app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

_load_error = None

try:
    from app import app
except Exception as e:
    _load_error = traceback.format_exc()
    # Create a minimal fallback Flask app that shows the real error
    app = Flask(__name__)

    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def show_error(path):
        return (
            f"<pre style='font-family:monospace;padding:20px'>"
            f"<b>STARTUP ERROR — fix this to get the app running:</b>\n\n"
            f"{_load_error}"
            f"</pre>",
            500
        )
