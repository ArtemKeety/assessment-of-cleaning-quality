from internal.middleware import SwaggerAuth
from fastapi import APIRouter, Depends, Request
from configuration import SwaggerCredential as Cred
from fastapi.openapi.docs import get_swagger_ui_html


swagger_router = APIRouter(
    include_in_schema=False,
    dependencies=[
        Depends(SwaggerAuth(login=Cred.login, password=Cred.password)),
    ]
)


@swagger_router.get('/docs')
async def docs(r: Request):
    return get_swagger_ui_html(openapi_url="/openapi.json", title=r.app.title)

@swagger_router.get('/openapi.json')
async def openapi(r: Request):
    return r.app.openapi()