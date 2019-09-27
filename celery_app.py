import os
from celery import Celery

REDIS_URI = os.getenv('CELERY_BROKER_URL')

app = Celery('celery_performance',
             backend=REDIS_URI,
             broker=REDIS_URI)