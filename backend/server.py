"""
Server entry point for the backend application.
This file is used by uvicorn to start the FastAPI application.
"""
import sys
import os

# Add parent directory to path so 'backend' module can be imported
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.main import app

# This allows uvicorn to start the app with: uvicorn server:app
