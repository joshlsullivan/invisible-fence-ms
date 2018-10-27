web: gunicorn invisible_fence.wsgi --log-file -
worker: celery -A invisible_fence worker
beat: celery -A invisible_fence beat -S django
