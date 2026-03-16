from typing import Annotated
from secrets import compare_digest
from dataclasses import dataclass, field
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials


SwaggerData = Annotated[HTTPBasicCredentials, Depends(HTTPBasic())]


@dataclass(slots=True, frozen=True)
class SwaggerAuth:
    login: str = field(init=True)
    password: str = field(init=True)


    def __call__(self, data: SwaggerData):
        if not compare_digest(data.username, self.login):
            raise HTTPException(status_code=401, detail="Login incorrect")

        if not compare_digest(data.password, self.password):
            raise HTTPException(status_code=401, detail="Password incorrect")

        return data


