from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app.routers import twitter
from app.routers import ph 

class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None


app = FastAPI()
app.include_router(
    twitter.router,
    prefix='/twitter'
)
app.include_router(
    ph.router,
    prefix='/ph'
)


@app.get("/")
async def index():
    return 'Hello World'