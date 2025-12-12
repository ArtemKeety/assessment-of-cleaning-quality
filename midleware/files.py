import os
import uuid
from fastapi_babel import _
from fastapi import UploadFile
from configuration import FILE_SIZE
from midleware import CustomHTTPException

class ValidateFiles:

    __slots__  = ("count", "patterns", "size")

    def __init__(self, count: int = 10, size: int = FILE_SIZE, *pattern:str):
        self.count = count
        self.patterns = pattern if pattern else (".jpg", ".png")
        self.size = size


    async def __call__(self, photos: list[UploadFile]) -> list[UploadFile]:
        if len(photos) > self.count:
            raise CustomHTTPException(status_code=400, detail=_("Too many photos"))

        for photo in photos:

            if not photo.filename.endswith(self.patterns):
                raise CustomHTTPException(status_code=400, detail=_("Unnecessary data format file") + f" '{photo.filename}'")

            if photo.size > self.size:
                raise CustomHTTPException(status_code=413, detail=f"'{photo.filename}' " + _("is big file"))

            photo.filename = f"{uuid.uuid4()}{os.path.splitext(photo.filename)[-1]}"

        return photos






