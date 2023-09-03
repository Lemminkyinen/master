from enum import Enum
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
import datetime as dt
from typing import Optional
from proxy import NasaAPI

app = FastAPI()
nasa_api = NasaAPI("")


class Response(BaseModel):
    b64_img: bytes
    url: str


@app.get("/picture-of-the-day")
def picture_of_the_day(date: Optional[dt.date] = dt.date.today()):
    if date < dt.date(1995, 5, 16):
        raise HTTPException(
            404,
            "Date must be after 1995-05-16, the first day an APOD picture was posted",
        )
    if date > dt.date.today():
        raise HTTPException(404, "There are no images for the future")
    content = nasa_api.get_picture_of_the_day(date)
    return Response(b64_img=content.base64_img, url=content.hdurl)
