from celery import Celery
from datetime import timedelta
from celery.schedules import crontab
import os
backend=os.getenv('CELERY_BACKEND','redis://127.0.0.1:6379/1')
broker=os.getenv('CELERY_BROKER','redis://127.0.0.1:6379/2')
celery=Celery('test',backend=backend,broker=broker,include=['celery_task.task'])


celery.conf.timezone='Asia/Shanghai'
celery.conf.enable_utc=False


# celery.conf.beat_schedule={
#     'add':{
#         'task':'celery_task.task.add',
#         'schedule':timedelta(seconds=10),
#         # 'schedule':crontab(hour=19,minute=0,day_of_week='*'),
#         'args':(1,5)
#     }
# }

# celery -A celery_task worker -l info  -n worker1.%h -P eventlet --concurrency=20 --max-tasks-per-child=20
# celery -A celery_task beat -l info