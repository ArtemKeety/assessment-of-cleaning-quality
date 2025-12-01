import asyncio
import aiofiles
from io import BytesIO
from fastapi import UploadFile


async def download_byte_from_UploadFile(photo: UploadFile) -> BytesIO:
    stream = BytesIO()
    while chunk := await photo.read(1024*1024):
        stream.write(chunk)

    stream.seek(0)
    return stream


async def bytes_from_UploadFile(photos: list[UploadFile])-> list[BytesIO]:
    tasks = [asyncio.create_task(download_byte_from_UploadFile(photo)) for photo in photos]
    return await asyncio.gather(*tasks)


async def download_byte_from_file(path:str)-> BytesIO:
    async with aiofiles.open(path, 'rb') as file:
        stream = BytesIO()
        while chunk := await file.read(1024*1024):
            stream.write(chunk)

    stream.seek(0)
    return stream


async def bytes_from_files(paths: list[str])-> list[BytesIO]:
    tasks = [asyncio.create_task(download_byte_from_file(path)) for path in paths]
    return await asyncio.gather(*tasks)