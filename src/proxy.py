from datetime import date
from requests import get
from typing import Optional
from pydantic import BaseModel
from dataclasses import dataclass
from fastapi import HTTPException
from base64 import b64encode


class NasaAPI:
    @dataclass
    class APODResponse:
        date: date
        title: str
        explanation: str
        hdurl: str
        url: str
        media_type: str
        service_version: str

    class Content(BaseModel):
        b64_img: bytes
        url: str

    apod_url: str = "https://api.nasa.gov/planetary/apod"
    apod_key: str

    def __init__(self, key):
        self.apod_key = key

    def build_apod_response(self, response: dict) -> APODResponse:
        return self.APODResponse(
            response["date"],
            response["title"],
            response["explanation"],
            response["hdurl"],
            response["url"],
            response["media_type"],
            response["service_version"],
        )

    def get_picture_of_the_day(self, d: date) -> bytes:
        params = {"api_key": self.apod_key, "date": d}
        response = get(
            self.apod_url,
            params=params,
        )
        if response.status_code != 200:
            raise HTTPException(404, "Cannot download image from NASA server")
        apod_r = self.build_apod_response(response.json())
        img_content = get(apod_r.hdurl).content
        return self.Content(
            b64_img=b64encode(img_content).decode("utf-8"), url=apod_r.hdurl
        )
