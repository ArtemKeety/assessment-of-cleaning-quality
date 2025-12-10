from customlogger import LOGGER
from pydantic import ValidationError
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse



class CustomHTTPException(HTTPException):
    def __init__(self, status_code: int = 400, detail=None):
        super().__init__(status_code, detail)


class ErrorHandler:

    @staticmethod
    def CustomHTTPException(request: Request, exception: HTTPException):
        return JSONResponse(
            status_code=exception.status_code,
            content={"message": exception.detail},
        )

    @staticmethod
    def UniqueViolationError(request: Request, exception: Exception):
        return JSONResponse(
            status_code=409,
            content={
                "message": "violation of the terms",
                "error": f"{type(exception).__name__}:{exception}"
            }
        )

    @staticmethod
    async def PydenticValidationError(request: Request, exception: ValidationError):
        errors = exception.errors()
        msg = [f"{error.get("loc", [0])[-1]}: {error.get("msg", "")}\n" for error in errors]
        return JSONResponse(
            status_code=400,
            content={"message": msg},
        )

    @staticmethod
    async def ConnectionError(request: Request, exception: ConnectionError):
        LOGGER.error(f"{type(exception).__name__}:{exception}")
        return JSONResponse(
            status_code=500,
            content={
                "message": "connection error",
                "error": f"{type(exception).__name__}:{exception}"
            }
        )

    @staticmethod
    async def Panic(request: Request, exception: Exception):
        LOGGER.error(f"{type(exception).__name__}:{exception}")
        return JSONResponse(
            status_code=500,
            content={
                "message": "An unexpected error has occurred",
            }
        )



