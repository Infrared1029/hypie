import pathlib

import htpy
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse


from .CounterWidget import CounterWidget


app = FastAPI()

app.mount(
    "/static", StaticFiles(directory=pathlib.Path(__file__).parent.resolve() / "static")
)


@app.get("/")
def counter_example(count: int = 0):
    return HTMLResponse(
        htpy.html[
            htpy.head[
                htpy.link(),
                htpy.link(rel="stylesheet", href="/static/_hypie_styles.css"),
                htpy.script(src="https://cdn.jsdelivr.net/npm/hyperscript.org@0.9.93"),
                htpy.title["Counter Example"],
            ],
            htpy.body[CounterWidget(count)],
        ]
    )
