import multiprocessing
import os

bind = f"0.0.0.0:{os.environ.get('PORT', '5000')}"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
timeout = 300
keepalive = 5
max_requests = 1000
max_requests_jitter = 50

