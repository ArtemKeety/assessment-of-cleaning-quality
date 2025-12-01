from .base import Base
from pydantic import model_validator, Field, ValidationError


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
            raise ValidationError('Passwords do not equal')
        return self


