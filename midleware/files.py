import uuid
import os
from fastapi import UploadFile
from configuration import FILE_SIZE
from midleware import CustomHTTPException


async def valid_files(photos: list[UploadFile]) -> list[UploadFile]:
    if len(photos) > 10:
        raise CustomHTTPException(status_code=400, detail="Too many photos")

    for photo in photos:

        if not photo.filename.endswith((".jpg", ".png")):
            raise CustomHTTPException(status_code=400, detail=f"Unnecessary data formats {photo.filename}")

        if photo.size > FILE_SIZE:
            raise CustomHTTPException(status_code=413, detail=f"{photo.filename} is big file")

        photo.filename = f"{uuid.uuid4()}{os.path.splitext(photo.filename)[-1]}"

    return photos



