"""
WSGI entry point for production deployment with Gunicorn
"""
import os
from threading import Thread
from api import app, ensure_articles_dir, scheduler_worker, generate_article_task

# Ensure articles directory exists on import
ensure_articles_dir()

# Start background scheduler (runs once when module is imported)
scheduler_thread = Thread(target=scheduler_worker, daemon=True)
scheduler_thread.start()
print("Background scheduler started in production mode.")

# Generate initial article (only once on startup)
# This will run when the WSGI server starts
try:
    print("Generating initial article in production...")
    generate_article_task()
except Exception as e:
    print(f"Error generating initial article: {e}")

# Export app for Gunicorn
__all__ = ['app']
