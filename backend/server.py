"""
Server entry point for the backend application.
This file is used by uvicorn to start the FastAPI application.
"""
from backend.main import app

# This allows uvicorn to start the app with: uvicorn server:app
