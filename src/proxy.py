import asyncio
import datetime as dt
import math
import random

# from base64 import b64encode
from dataclasses import dataclass
from itertools import chain

import httpx
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
    search_url: str = "https://images-api.nasa.gov/search"
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

    async def get_pod_url(self, date: dt.date) -> str:
        params = {"api_key": self.api_key, "date": date}
        async with httpx.AsyncClient() as client:
            response = await client.get(
                self.apod_url,
                params=params,
            )

            if response.status_code != 200:
                print(response.json())
                raise HTTPException(response.status_code, response.json().get("msg"))
            content = self.build_content(response.json())
        # img_content = get(content.hdurl).content
        # content.base64_img = b64encode(img_content).decode("utf-8")
        return content.hdurl

    def get_mars_rover_info(self, rover: m.Rover) -> m.RoverInfo:
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

    async def _get_pictures(self, rover: m.RoverInfo, params: dict) -> list:
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.mars_url}/{rover.name}/photos", params=params
                )
                if response.status_code != 200:
                    error_data = response.json()
                    raise HTTPException(response.status_code, error_data.get("msg"))

                photos = response.json()["photos"]
                img_src_list = list(map(lambda photo: photo["img_src"], photos))
                return img_src_list
            except Exception as e:
                print(f"An error occurred: {e}")
                return []

    async def get_mars_picture_urls(
        self, rover: m.RoverInfo, date: dt.date
    ) -> list[str]:
        futures = []
        image_urls = []
        for camera in rover.cameras:
            params = {
                "api_key": self.api_key,
                "earth_date": date,
                "camera": camera,
            }
            future = asyncio.ensure_future(self._get_pictures(rover, params))
            futures.append(future)
        results = await asyncio.gather(*futures)
        image_urls.extend(results)
        return list(chain.from_iterable(image_urls))

    async def get_random_image_url(self) -> str:
        year = str(random.choice(range(1960, 2023)))
        item_index = random.choice(range(0, 10))
        page_size = 10

        params = {
            # "api_key": self.api_key,
            "media_type": "image",
            "page_size": page_size,
            "year_start": year,
            "year_end": year,
        }
        async with httpx.AsyncClient() as client:
            response = await client.get(self.search_url, params=params)
            if response.status_code != 200:
                error_data = response.json()
                raise HTTPException(response.status_code, error_data.get("msg"))
            data = response.json()["collection"]
            total_hits = data["metadata"]["total_hits"]
            pages = math.ceil(total_hits / page_size)
            page = random.choice(range(1, pages))
            params["page"] = page

            response = await client.get(self.search_url, params=params)
            if response.status_code != 200:
                error_data = response.json()
                raise HTTPException(response.status_code, error_data.get("msg"))
            item = response.json()["collection"]["items"][item_index]
            response = await client.get(item["href"])
            if response.status_code != 200:
                error_data = response.json()
                raise HTTPException(response.status_code, error_data.get("msg"))
            hrefs = response.json()
            print(hrefs)
            url = next(filter(lambda url: url[-3:] == "jpg", hrefs))

        return url
