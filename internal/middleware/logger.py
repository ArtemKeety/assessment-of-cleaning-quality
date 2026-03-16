import time
from fastapi import Request
from customlogger import FabricLogger
from starlette.middleware.base import BaseHTTPMiddleware


class LogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        method = FabricLogger(response.status_code)

        method(
            f"{request.client.host}:{request.client.port} - - [{time.strftime('%d/%b/%Y:%H:%M:%S %z')}] "
            f"\"{request.method} {request.url.path} {request.scope.get('http_version', '1.1')}\" "
            f"{response.status_code} {len(response.body) if hasattr(response, 'body') else 0} "
            f"\"{request.headers.get('referer', '')}\" \"{request.headers.get('user-agent', '')}\""
        )
        return response



