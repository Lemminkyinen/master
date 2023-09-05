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
    url = await nasa_api.get_pod_url(date)
    return m.Response(msg="ok", url=[url])


@app.get("/mars/{rover}")
async def mars_rover(rover: m.Rover, date: dt.date | None = None) -> m.Response:
    if date is None:
        date = dt.date.today()
    rover_info = nasa_api.get_mars_rover_info(rover)
    if not rover_info.min_date <= date <= rover_info.max_date:
        raise HTTPException(
            422,
            f"For {rover_info.name} rover use date between "
            f"{rover_info.min_date} - {rover_info.max_date}",
        )
    future = nasa_api.get_mars_picture_urls(rover_info, date)
    urls = await future
    return m.Response(msg="ok", url=urls)


@app.get("/random")
async def random_image() -> m.Response:
    pass
