from celery import Celery
from configuration import CeleryConfig
from configuration import RedisConfig

celery_app = Celery(
    'celery_app',
    broker=str(RedisConfig()),
    backend=str(RedisConfig()),
    include=['tasks.req_ai'],
)
celery_app.config_from_object(CeleryConfig, namespace='CELERY')
celery_app.autodiscover_tasks(['tasks'], force=True)