from enum import Enum
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, Path, Query
from datetime import date

app = FastAPI()


@app.get("/picture-of-the-day")
def picture_of_the_day(d: date):
    pass
