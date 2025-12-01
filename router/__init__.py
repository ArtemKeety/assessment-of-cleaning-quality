from .user import router as user_router
from .flat import router as flat_router
from .report import router as report_router

__all__ = [
    'user_router',
    "flat_router",
    'report_router',
]