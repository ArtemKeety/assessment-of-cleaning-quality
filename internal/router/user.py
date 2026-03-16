from database import RedisSession
from .dependecies import LayerDep, UserAgent
from fastapi import APIRouter, Response, Depends
from internal.middleware import UserIdenty, user_identy
from internal.shemas import UserRegister, UserLogin, Session
from configuration import LIFE_TIME, HTTP_ONLY, SECURE_CONNECTION


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
        redis: RedisSession,
        user_data: UserIdenty
):
    await redis.delete(user_data.get('session'))
    res.delete_cookie('session')
    return {"message": "success"}


@router.delete("/delete", response_model=None, status_code=204)
async def delete(
        res: Response,
        redis: RedisSession,
        user_data: UserIdenty,
        service: LayerDep,
):
    await redis.delete(user_data.get('session'))
    res.delete_cookie('session')
    return await service.User.del_user(user_data.get('user_id'))


@router.get("/check-auth", dependencies=[Depends(user_identy)], include_in_schema=False)
async def check_auth():
    return {"message": "success"}