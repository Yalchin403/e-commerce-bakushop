from __future__ import absolute_import, unicode_literals
from celery import Celery
import os
import logging


LOGGER = logging.getLogger(__name__)


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'order_automation.settings')

app = Celery('order_automation')

app.config_from_object('django.conf:settings', namespace='CELERY')


app.conf.timezone = 'Asia/Baku'

app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    LOGGER.debug('Request: {0!r}'.format(self.request))
