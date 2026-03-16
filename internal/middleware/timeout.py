import asyncio
from fastapi import Request
from starlette.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware


class TimeoutMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, timeout:int):
        super().__init__(app)
        self.timeout = timeout

    async def dispatch(self, request: Request, call_next):
        try:
            return await asyncio.wait_for(call_next(request), self.timeout)
        except asyncio.TimeoutError:
            return JSONResponse(
                content={"message": "Request timed out"},
                status_code=408
            )




