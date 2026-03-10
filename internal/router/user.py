from database import RedisSession
from .dependecies import LayerDep, UserAgent
from internal.midleware import UserIdenty, user_identy
from fastapi import APIRouter, Response, Depends, Query
from configuration import LIFE_TIME, HTTP_ONLY, SECURE_CONNECTION
from internal.shemas import UserRegister, UserLogin, Session, UserRole


router = APIRouter(prefix="/api/v1")


@router.post("/sign-up", response_model=Session)
async def sign_up(
        r: UserRegister,
        res: Response,
        agent: UserAgent,
        service: LayerDep,
        redis: RedisSession
)-> Session:
    s: Session = await service.User.sign_up(r, agent, redis)
    res.set_cookie(
        'session',
        value=s.session,
        max_age=LIFE_TIME,
        httponly=HTTP_ONLY,
        expires=LIFE_TIME,
        secure=SECURE_CONNECTION,
    )
    return s

@router.post("/sign-in", response_model=Session)
async def sign_in(
        u: UserLogin,
        res: Response,
        agent: UserAgent,
        service:LayerDep,
        redis: RedisSession
)-> Session:
    s: Session = await service.User.sign_in(u, agent, redis)
    res.set_cookie(
        'session',
        value=s.session,
        max_age=LIFE_TIME,
        httponly=HTTP_ONLY,
        expires=LIFE_TIME,
        secure=SECURE_CONNECTION,
    )
    return s

@router.post("/logout")
async def logout(
        res: Response,
        user: UserIdenty,
        redis: RedisSession,
):
    await redis.delete(user.session)
    res.delete_cookie('session')
    return {"message": "success"}


@router.delete("/delete", response_model=None, status_code=204)
async def delete(
        res: Response,
        user: UserIdenty,
        service: LayerDep,
        redis: RedisSession,
):
    await redis.delete(user.session)
    res.delete_cookie('session')
    return await service.User.del_user(user)


@router.get("/change-role")
async def change_role(user: UserIdenty, service: LayerDep, redis: RedisSession, role: UserRole=Query()):
    return await service.User.add_role(user, role.role, redis)


@router.get("/check-auth", dependencies=[Depends(user_identy)], include_in_schema=False)
async def check_auth():
    return {"message": "success"}