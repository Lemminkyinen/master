import datetime as dt
from typing import Annotated

from fastapi import FastAPI, HTTPException, Query

import models as m
from proxy import NasaAPI

app = FastAPI()
nasa_api = NasaAPI("")


@app.get("/picture-of-the-day")
async def picture_of_the_day(
    date: Annotated[
        dt.date | None, Query(gt=dt.date(1995, 5, 16), le=dt.date.today())
    ] = None
) -> m.Response:
    if date is None:
        date = dt.date.today()
    content = await nasa_api.get_picture_of_the_day(date)
    return m.Response(b64_img=content.base64_img, url=content.hdurl)


@app.get("/mars/{rover}")
async def mars_rover(rover: m.Rover, date: dt.date | None = None) -> dict:
    if date is None:
        date = dt.date.today()
    rover_info = await nasa_api.get_mars_rover_info(rover)
    if not rover_info.min_date <= date <= rover_info.max_date:
        raise HTTPException(
            422,
            f"For {rover_info.name} rover use date between "
            f"{rover_info.min_date} - {rover_info.max_date}",
        )

    return {"msg": "ok"}
