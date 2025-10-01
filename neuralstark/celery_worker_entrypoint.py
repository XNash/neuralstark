import eventlet
eventlet.monkey_patch()

from neuralstark.celery_app import celery_app