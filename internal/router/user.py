from database import RedisDb
from internal.service import Service
from fastapi import APIRouter, Depends, Response
from internal.midleware import get_header_data, user_identy
from internal.shemas import UserRegister, UserLogin, Session
from configuration import LIFE_TIME, HTTP_ONLY, SECURE_CONNECTION


router = APIRouter(prefix="/user")


@router.post("/sign-up", response_model=Session)
async def sign_up(
        r: UserRegister,
        res: Response,
        agent: str = Depends(get_header_data),
        service = Depends(Service.from_request),
        redis: RedisDb = Depends(RedisDb.from_request_conn)
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
        agent: str = Depends(get_header_data),
        service = Depends(Service.from_request),
        redis: RedisDb = Depends(RedisDb.from_request_conn)
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
        redis: RedisDb = Depends(RedisDb.from_request_conn),
        user_data = Depends(user_identy)
):
    await redis.delete(user_data.get('session'))
    res.delete_cookie('session')
    return {"message": "success"}


@router.delete("/delete", response_model=int)
async def delete(
        res: Response,
        redis: RedisDb = Depends(RedisDb.from_request_conn),
        user_data = Depends(user_identy),
        service = Depends(Service.from_request),
):
    await redis.delete(user_data.get('session'))
    res.delete_cookie('session')
    return await service.del_user(user_data.get('user_id'))


@router.get("/check-auth", dependencies=[Depends(user_identy)], include_in_schema=False)
async def check_auth():
    return {"message": "success"}