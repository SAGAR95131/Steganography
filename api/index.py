import sys
import os
import traceback

# Add the parent directory to path so we can import app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from app import app
    application = app
except Exception as e:
    # If the app fails to load, return the error as a plain HTTP response
    # so we can see exactly what's crashing
    error_details = traceback.format_exc()

    def app(environ, start_response):
        status = '500 Internal Server Error'
        headers = [('Content-Type', 'text/plain')]
        start_response(status, headers)
        body = f"STARTUP ERROR:\n\n{str(e)}\n\n--- Full Traceback ---\n{error_details}"
        return [body.encode('utf-8')]

    application = app
