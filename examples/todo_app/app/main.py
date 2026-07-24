import random
import pathlib
from typing import Annotated

from fastapi import FastAPI, Body
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

from .ui.pages.TodoAppPage import TodoAppPage
from .ui.widgets.components.TodoItem.TodoItem import TodoItem


app = FastAPI()

db = {
    "todos": [
        {"id": 1, "title": "Do Laundry", "done": True},
        {"id": 2, "title": "Study", "done": False},
    ]
}


app.mount(
    "/static",
    StaticFiles(directory=pathlib.Path(__file__).parent / "static"),
    name="static",
)


@app.get("/")
def get():
    return HTMLResponse(TodoAppPage(db["todos"]))


@app.patch("/toggle/{tid}")
def toggle_todo(tid: int):
    for todo in db["todos"]:
        if todo["id"] == tid:
            todo["done"] = not todo["done"]
            return HTMLResponse(TodoItem(**todo))


@app.delete("/{tid}")
def delete_todo(tid: int):
    db["todos"] = [t for t in db["todos"] if t["id"] != tid]


@app.post("/")
def create_todo_(title: Annotated[str, Body(embed=True)]):
    id = random.randint(0, 1_000_000)
    db["todos"].append({"id": id, "title": title, "done": False})
    return HTMLResponse(TodoItem(id=id, title=title, done=False))
