import time
import requests
from functools import wraps
from customlogger import LOGGER


class CustomRetry:

    __slots__ = ('count', 'delay', 'backoff', 'exceptions')

    def __init__(self, count: int, delay: int = 1, backoff: int = 2, *exc: Exception):
        self.count = count
        self.delay = delay
        self.backoff = backoff
        self.exceptions = exc or (Exception, )

    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            error = None
            for attempt in range(self.count):
                try:
                    return func(*args, **kwargs)
                except self.exceptions as e:
                    error = e
                    times = self.delay * (self.backoff ** attempt)
                    LOGGER.error(f"{type(e).__name__}: {e}, sleeping {times} seconds")
                    time.sleep(times)
            raise error
        return wrapper