import pathlib

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from .ui.pages.app import CartApp
import requests

app = FastAPI()

app.mount(
    "/static", StaticFiles(directory=pathlib.Path(__file__).resolve().parent / "static")
)

products = [
    {"id": p["id"], "title": p["title"], "price": p["price"], "image_url": p["image"]}
    for p in requests.get("https://fakestoreapi.com/products?limit=10").json()
]


@app.get("/")
def index():
    app = CartApp(products=products)
    return HTMLResponse(app)
