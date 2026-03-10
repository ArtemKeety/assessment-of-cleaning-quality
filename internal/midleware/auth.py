from fastapi_babel import _
from typing import Annotated
from database import RedisSession
from secrets import compare_digest
from .error import CustomHTTPException
from fastapi import Request, Depends, Response
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from configuration import LIFE_TIME, HTTP_ONLY, SECURE_CONNECTION, ROLE_TIME
from internal.domain import Role, UserDomain


secure = HTTPBearer(auto_error=False)

Credentials = Annotated[HTTPAuthorizationCredentials, Depends(secure)]

async def user_identy(
        request: Request,
        response: Response,
        credentials: Credentials,
)-> UserDomain:
    session = request.cookies.get("session")

    if not session and credentials and credentials.scheme.lower() == "bearer":
        session = credentials.credentials

    if not session:
        raise CustomHTTPException(status_code=401, detail=_("Not found credentials"))

    redis: RedisSession = request.app.state.redis_pool

    if not (data := await redis.get(session)):
        raise CustomHTTPException(status_code=401, detail=_("Out of session"))

    if not compare_digest(request.headers.get("User-Agent"), data.get("User-Agent")):
        raise CustomHTTPException(status_code=401, detail=_("User-Agent not match"))

    if not (role := await redis.get(f"role:{data["user_id"]}")):
        role = {"role": Role.default}

    user: UserDomain = UserDomain(session=session, id=data["user_id"],role=Role(role["role"]))

    await redis.new_expire(session)

    response.set_cookie(
        "session",
        value=session,
        max_age=LIFE_TIME,
        httponly=HTTP_ONLY,
        expires=LIFE_TIME,
        secure=SECURE_CONNECTION,
    )

    request.state.user_id = user.id

    return user

UserIdenty = Annotated[UserDomain,  Depends(user_identy)]










