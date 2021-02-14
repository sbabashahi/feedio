import os

from celery import Celery
from celery.schedules import crontab


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'feedio.settings.development')

app = Celery('feedio', broker='redis://localhost')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks(['utils'])
app.conf.beat_schedule = {
    # Executes every day at  12:30 pm.
    'run-every-hour': {
        'task': 'utils.tasks.check_rss_every_hour',
        'schedule': crontab(hour='*/1', minute=0),
        'args': (),
    },
}
