"""
WSGI entry point for production deployment with Gunicorn
"""
import os
from threading import Thread
from api import app, scheduler_worker

# Start background scheduler (runs once when module is imported)
scheduler_thread = Thread(target=scheduler_worker, daemon=True)
scheduler_thread.start()
print("Background scheduler started in production mode.")
print("Articles will be generated every 30 minutes and saved to Supabase.")

# Export app for Gunicorn
__all__ = ['app']
