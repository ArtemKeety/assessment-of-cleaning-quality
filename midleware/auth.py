from database import RedisDb
from secrets import compare_digest
from .error import CustomHTTPException
from fastapi import Request, Depends, Response
from configuration import LIFE_TIME, HTTP_ONLY, SECURE_CONNECTION
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer


secure = HTTPBearer(auto_error=False)


async def user_identy(request: Request, response: Response, credentials: HTTPAuthorizationCredentials = Depends(secure)):
    session = request.cookies.get("session")

    if not session and credentials and credentials.scheme.lower() == "bearer":
        session = credentials.credentials

    if not session:
        raise CustomHTTPException(status_code=401, detail="Not found credentials")

    redis: RedisDb = request.app.state.redis_pool

    if not (data := await redis.get(session)):
        raise CustomHTTPException(status_code=401, detail="Out of session")

    if not compare_digest(request.headers.get("User-Agent"), data.get("User-Agent")):
        raise CustomHTTPException(status_code=401, detail="User-Agent not match")

    data.update({"session": session})

    await redis.new_expire(session)

    response.set_cookie(
        "session",
        value=session,
        max_age=LIFE_TIME,
        httponly=HTTP_ONLY,
        expires=LIFE_TIME,
        secure=SECURE_CONNECTION,
    )

    return data




