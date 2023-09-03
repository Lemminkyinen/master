import datetime as dt
from base64 import b64encode
from dataclasses import dataclass

from fastapi import HTTPException
from requests import get

import models as m


class NasaAPI:
    @dataclass
    class Content:
        date: dt.date
        title: str
        explanation: str
        hdurl: str
        url: str
        media_type: str
        service_version: str
        base64_img: bytes | None = None

    apod_url: str = "https://api.nasa.gov/planetary/apod"
    mars_url: str = "https://api.nasa.gov/mars-photos/api/v1/rovers"
    api_key: str

    def __init__(self, key):
        if len(key) == 0:
            print("API KEY IS MISSING")
        self.api_key = key

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

    async def get_picture_of_the_day(self, date: dt.date) -> Content:
        params = {"api_key": self.api_key, "date": date}
        response = get(
            self.apod_url,
            params=params,
        )
        if response.status_code != 200:
            print(response.json())
            raise HTTPException(response.status_code, response.json().get("msg"))
        content = self.build_content(response.json())
        img_content = get(content.hdurl).content
        content.base64_img = b64encode(img_content).decode("utf-8")
        return content

    async def get_mars_rover_info(self, rover: m.Rover) -> m.RoverInfo:
        params = {"api_key": self.api_key}
        response = get(f"{self.mars_url}/{rover.name}", params=params)
        if response.status_code != 200:
            print(response.json())
            raise HTTPException(response.status_code, response.json().get("msg"))
        data = response.json()["rover"]
        cameras = list(map(lambda c: c["name"].lower(), data["cameras"]))
        min_date = dt.date.fromisoformat(data["landing_date"])
        max_date = dt.date.fromisoformat(data["max_date"])
        return m.RoverInfo(rover.name, cameras, min_date, max_date)

    async def get_mars_pictures(self, rover: m.RoverInfo, date: dt.date) -> Content:
        params = {
            "api_key": self.api_key,
            "earth_date": date,
            "camera": "",
        }
        for camera in rover.cameras:
            params["camera"] = camera
            response = get(f"{self.mars_url}/{rover.name}/photos", params=params)
