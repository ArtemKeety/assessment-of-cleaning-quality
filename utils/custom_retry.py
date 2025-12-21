import time
import requests
from functools import wraps
from customlogger import LOGGER


class CustomRetry:

    __slots__ = ('count', 'max_times')

    def __init__(self, count: int, max_times: int):
        self.count = count
        self.max_times = max_times

    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            error = None
            chunk = self.max_times / self.count
            for i in range(self.count):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    error = e
                    LOGGER.error(f"{type(e).__name__}: {e}")
                    times = (i + 1) * chunk
                    time.sleep(times)
            raise requests.RequestException(f"{type(error).__name__}: {error}")
        return wrapper