import os
from fastapi import Depends
from dotenv import load_dotenv
from secrets import compare_digest
from .error import CustomHTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials

load_dotenv()

user_name = os.getenv("swagger_name")
password = os.getenv("swagger_pass")

security = HTTPBasic()


def swagger_auth(c: HTTPBasicCredentials = Depends(security)):
    if not c:
        raise CustomHTTPException(status_code=401, detail="Invalid credentials for swagger")

    if not compare_digest(c.password, password) or not compare_digest(c.username, user_name):
        raise CustomHTTPException(status_code=401, detail="Invalid credentials for swagger")

    return c
