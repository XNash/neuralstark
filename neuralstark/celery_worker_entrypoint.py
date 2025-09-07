import gevent.monkey
gevent.monkey.patch_all()

from neuralstark.celery_app import celery_app
