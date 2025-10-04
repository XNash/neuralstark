import gevent.monkey
gevent.monkey.patch_all()

from backend.celery_app import celery_app
