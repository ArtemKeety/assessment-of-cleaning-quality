import re
from .base import Base
from fastapi_babel import _
from internal.midleware import CustomHTTPException
from pydantic import model_validator, Field, field_validator


class UserLogin(Base):
    login:str = Field(min_length=3, max_length=25)
    password:str = Field(min_length=3, max_length=25)


class User(Base):
    id: int
    is_active: bool
    login:str = Field(min_length=3, max_length=255)
    password:str = Field(min_length=3, max_length=255)


class UserRegister(UserLogin):
    confirm:str = Field(min_length=3, max_length=25)

    @model_validator(mode='after')
    def verify(self) -> 'UserRegister':
        if self.password != self.confirm:
            raise CustomHTTPException(detail=_('Passwords do not equal'), status_code=400)
        return self


    @field_validator('password')
    def validate_password(cls, value:str) -> str:
        pattern4 = r'[' + re.escape('!@#$%^&*') + r']'
        if not re.search(pattern4, value):
            raise CustomHTTPException(detail=_('Password must have been complicated'), status_code=400)
        return value

