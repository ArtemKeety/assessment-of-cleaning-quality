from celery_app import celery_app
from typing import Any

def get_status(s: str) -> tuple[str, dict[str, Any]]:
    result = celery_app.AsyncResult(s)
    return result.state, result.info