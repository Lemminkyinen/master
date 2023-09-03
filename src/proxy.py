from datetime import date
from requests import get
from typing import Optional
from pydantic import BaseModel
from dataclasses import dataclass
from fastapi import HTTPException
from base64 import b64encode


class NasaAPI:
    @dataclass
    class Content:
        date: date
        title: str
        explanation: str
        hdurl: str
        url: str
        media_type: str
        service_version: str
        base64_img: bytes | None = None

    apod_url: str = "https://api.nasa.gov/planetary/apod"
    apod_key: str

    def __init__(self, key):
        if len(key) == 0:
            print("API KEY IS MISSING")
        self.apod_key = key

    def build_content(self, response: dict) -> Content:
        return self.Content(
            response["date"],
            response["title"],
            response["explanation"],
            response["hdurl"],
            response["url"],
            response["media_type"],
            response["service_version"],
        )

    def get_picture_of_the_day(self, d: date) -> Content:
        params = {"api_key": self.apod_key, "date": d}
        response = get(
            self.apod_url,
            params=params,
        )
        if response.status_code != 200:
            print(response.json())
            raise HTTPException(404, "Cannot download image from NASA server")
        content = self.build_content(response.json())
        img_content = get(content.hdurl).content
        content.base64_img = b64encode(img_content).decode("utf-8")
        return content
