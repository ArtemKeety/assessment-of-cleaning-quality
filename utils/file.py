import os
import asyncio
import aiofiles
from fastapi import UploadFile


async def download_file(photo: UploadFile, directory: str):
    async with aiofiles.open(os.path.join(directory, photo.filename), mode='wb') as file:
        while chuck := await photo.read(1024 * 1024):
            await file.write(chuck)


async def download_files(photos: list[UploadFile], directory: str):
    tasks = [asyncio.create_task(download_file(photo, directory)) for photo in photos]
    await asyncio.gather(*tasks)




