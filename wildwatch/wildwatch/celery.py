import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wildwatch.settings')

app = Celery('wildwatch')
app.config_from_object('django.conf:settings')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'every-hour-startparcing': {
        'task': 'watch.tasks.find_vendor_codes_to_parse',
        'schedule': crontab(minute=0),
    },
}
