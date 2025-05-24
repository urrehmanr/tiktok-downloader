#!/usr/bin/env python3
"""
TikTok Downloader Runner

This script sets up the TikTok Downloader application and starts the Flask server.
"""

import os
import sys
import platform
import argparse
import threading
import webbrowser
from app import app

def create_required_directories():
    """Create necessary directories for the application."""
    directories = [
        'downloads',
        'templates',
        'static',
        'static/css',
        'static/js',
        'video_storage'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        
    return True

def check_required_files():
    """Check if all required files exist."""
    required_files = [
        'app.py',
        'templates/index.html',
        'templates/mp3.html',
        'static/js/app.js',
        'static/css/main.css',
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        return False, missing_files
    return True, []

def open_browser(port):
    """Open browser after a delay."""
    threading.Timer(1.5, lambda: webbrowser.open(f'http://localhost:{port}')).start()

def run_app(port=5000, debug=False, auto_open=True):
    """Run the Flask application."""
    # Create required directories
    create_required_directories()
    
    # Check required files
    files_ok, missing_files = check_required_files()
    if not files_ok:
        print(f"Error: Missing required files: {', '.join(missing_files)}")
        return False
    
    # Open browser if requested
    if auto_open:
        open_browser(port)
    
    # Run the Flask application
    app.run(host='0.0.0.0', port=port, debug=debug)
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run TikTok Downloader App')
    parser.add_argument('--port', type=int, default=5000, help='Port to run the app on')
    parser.add_argument('--debug', action='store_true', help='Run in debug mode')
    parser.add_argument('--no-browser', action='store_true', help='Don\'t open browser automatically')
    
    args = parser.parse_args()
    
    run_app(port=args.port, debug=args.debug, auto_open=not args.no_browser) 