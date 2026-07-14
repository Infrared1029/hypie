import pathlib
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from .ui.components import Layout, Counter


app = FastAPI()

app.mount(
    "/static", StaticFiles(directory=pathlib.Path(__file__).parent.resolve() / "static")
)


@app.get("/")
def counter_example():
    return HTMLResponse(Layout[Counter(5)])
