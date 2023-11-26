from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse
import aiofiles

import uuid
import os
from database.models import Media


router = APIRouter()


@router.post("")
async def post_tweet_media(file: UploadFile = File(...)) -> JSONResponse:
    media_content = await file.read()
    filename, file_extension = os.path.splitext(file.filename)
    unique_filename = "{}_{}{}".format(filename, uuid.uuid4(), file_extension)
    media_path = f"/medias/{unique_filename}"
    media = Media(media_path=media_path)
    media = await media.add()
    async with aiofiles.open(media_path, mode="wb") as media_file:
        await media_file.write(media_content)
    response = {"result": True, "media_id": media.id}
    return JSONResponse(content=response, status_code=201)
