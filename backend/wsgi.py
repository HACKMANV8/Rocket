#!/usr/bin/env python3
"""
WSGI entry point for production deployment
"""
import os
import sys

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, initialize_services

# Initialize services when the WSGI app loads
initialize_services()

# This makes the app available to WSGI servers
application = app

if __name__ == "__main__":
    # This allows running: python wsgi.py (for development)
    app.run(host='0.0.0.0', port=5000, debug=False)