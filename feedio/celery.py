import os

from celery import Celery
from celery.schedules import crontab
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'feedio.settings.development')

if settings.DEBUG:
    app = Celery('feedio', broker='redis://localhost')
else:
    app = Celery('feedio', broker='redis://redis')

app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks(['utils'])
app.conf.beat_schedule = {
    'run-every-hour': {
        'task': 'utils.tasks.check_rss_every_hour',
        'schedule': crontab(hour='*/1', minute=0),
        'args': (),
    },
}
