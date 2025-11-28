web: gunicorn api:app --bind 0.0.0.0:$PORT --workers 2 --timeout 300 --access-logfile - --error-logfile -
release: python -c "from api import ensure_articles_dir; ensure_articles_dir()"
