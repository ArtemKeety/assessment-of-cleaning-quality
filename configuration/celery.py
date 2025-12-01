from .db import RedisConfig


class CeleryConfig:
    CELERY_BROKER_URL = f"{RedisConfig()}"
    CELERY_RESULT_BACKEND = f"{RedisConfig()}"
    CELERY_TIMEZONE = 'UTC'
    CELERY_ACCEPT_CONTENT = ['application/json']
    CELERY_TASK_SERIALIZER = 'json'
    CELERY_RESULT_SERIALIZER = 'json'
    CELERY_BROKER_TRANSPORT_OPTIONS = {
        'visibility_timeout': 3600,  # 1 час
        'socket_keepalive': True,
        'retry_on_timeout': True,
        'socket_connect_timeout': 5,
        'max_retries': 3,
    }

    CELERY_BROKER_HEARTBEAT = 10  # seconds
    CELERY_BROKER_CONNECTION_TIMEOUT = 30  # seconds
    CELERY_BROKER_CONNECTION_RETRY = True
    CELERY_BROKER_CONNECTION_MAX_RETRIES = 3