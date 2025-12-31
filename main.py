import asyncpg
import logging
from fastapi import Depends
from fastapi import FastAPI
from granian import Granian
from internal.router import *
from customlogger import LOGGER
from internal.midleware import *
from internal.lifespan import LifeSpan
from granian.constants import Interfaces
from fastapi.staticfiles import StaticFiles
from fastapi_limiter.depends import RateLimiter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.exceptions import RequestValidationError
from fastapi_babel import Babel, BabelConfigs, BabelMiddleware
from configuration import TIMEOUT, FLAT_FILE_PATH, REPORT_FILE_PATH, RAW_REPORT_FILE_PATH, WORKERS


LOGGER.setLevel(logging.INFO)


app = FastAPI(
    lifespan=LifeSpan(FLAT_FILE_PATH, REPORT_FILE_PATH, RAW_REPORT_FILE_PATH),
    version="1.4.2",
    title="Оценка домашних дел",
    description="Приложение для помощи в оценке домашних дел",
    docs_url=None,
    openapi_url=None,
    redoc_url=None,
    dependencies=[Depends(RateLimiter(times=60, seconds=60))],
)

babel_configs = BabelConfigs(
    ROOT_DIR=__file__,
    BABEL_DEFAULT_LOCALE="en",
    BABEL_TRANSLATION_DIRECTORY="locales"
)

babel = Babel(configs=babel_configs)

origins = (
    "http://127.0.0.1:8000",
    "http://127.0.0.1:3000",
    "http://localhost:3000",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(LogMiddleware)
app.add_middleware(TimeoutMiddleware, TIMEOUT)
app.add_middleware(BabelMiddleware, babel_configs=babel_configs)

app.add_exception_handler(CustomHTTPException, ErrorHandler.CustomHTTPException)
app.add_exception_handler(asyncpg.UniqueViolationError, ErrorHandler.UniqueViolationError)
app.add_exception_handler(RequestValidationError, ErrorHandler.PydenticValidationError)
app.add_exception_handler(ConnectionError, ErrorHandler.ConnectionError)
app.add_exception_handler(Exception, ErrorHandler.Panic)

app.include_router(user_router, prefix="/api/v1", tags=["user"])
app.include_router(flat_router, prefix="/api/v1", tags=["flat"])
app.include_router(report_router, prefix="/api/v1", tags=["report"])

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get('/docs', include_in_schema=False, dependencies=[Depends(swagger_auth)])
async def docs():
    return get_swagger_ui_html(openapi_url="/openapi.json", title=app.title)

@app.get('/openapi.json', include_in_schema=False, dependencies=[Depends(swagger_auth)])
async def openapi():
    return app.openapi()


if __name__ == '__main__':
    server = Granian(
        target="main:app",
        interface=Interfaces.ASGI,
        workers=WORKERS,
        runtime_threads=8,
        address="0.0.0.0",
        port=8000,
    )
    server.serve()

