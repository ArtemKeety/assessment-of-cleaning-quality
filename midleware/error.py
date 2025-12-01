
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




