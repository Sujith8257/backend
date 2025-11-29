"""
WSGI entry point for production deployment with Gunicorn
"""
import os
from threading import Thread
from datetime import datetime
from api import app, scheduler_worker, generate_article_task

# Start background scheduler (runs once when module is imported)
scheduler_thread = Thread(target=scheduler_worker, daemon=True)
scheduler_thread.start()
print(f"[{datetime.now()}] ✅ Background scheduler started in production mode.")
print(f"[{datetime.now()}] ✅ Articles will be generated every 30 minutes and saved to Supabase.")

# Generate initial article on startup (after a short delay to ensure Supabase connection is ready)
def generate_initial_article():
    """Generate first article after a short delay"""
    import time
    time.sleep(5)  # Wait 5 seconds for app to fully initialize
    print(f"[{datetime.now()}] 🚀 Generating initial article on startup...")
    try:
        generate_article_task()
        print(f"[{datetime.now()}] ✅ Initial article generation completed.")
    except Exception as e:
        print(f"[{datetime.now()}] ❌ ERROR generating initial article: {str(e)}")
        import traceback
        traceback.print_exc()

# Start initial article generation in background
initial_article_thread = Thread(target=generate_initial_article, daemon=True)
initial_article_thread.start()

# Export app for Gunicorn
__all__ = ['app']
