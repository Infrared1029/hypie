<p align="center">
    <img src="https://raw.githubusercontent.com/Infrared1029/hypie/main/assets/hypie_logo.jpg" alt="Logo" width="400">
</p>

## Intro
Hypie, pronounced "high-pie", is a python library for building web frontends, built on top of [_hyperscript](https://github.com/bigskysoftware/_hyperscript), a scripting language for the web made by the [htmx](https://github.com/bigskysoftware/htmx) folks, and [htpy](https://github.com/pelme/htpy), a library for generating HTML in python.  

The goal of hypie is to be able to code powerful web frontends, server-side rendered or client-side rendered (or a mix of both), without having to leave python, or switch your favorite backend, using relatively little abstractions and no reactivity.

New README in the process, for now enjoy this counter example:
```python
import htpy
import hypie as hp


class CounterWidget(hp.ServerComponent):
    initial_count: int = 0

    def template(self):
        count_var = hp.var(":count")

        return htpy.div[
            htpy.button(
                _=hp.hs(
                    hp.set_(count_var, to=self.initial_count),
                    hp.On("click")[
                        hp.set_(count_var, to=count_var + 1),
                        hp.set_(hp.me.textContent, to=f"Count is: {count_var}"),
                    ],
                )
            )[f"Count is: {self.initial_count}"]
        ]


@hp.style(CounterWidget)
def counter_style():
    return {
        "button": {
            "background-color": "#4A90D9",
            "color": "#ffffff",
            "border": "none",
            "border-radius": "6px",
            "padding": "10px 20px",
            "font-size": "16px",
            "font-weight": "600",
            "cursor": "pointer",
            "transition": "background-color 0.2s ease",
        },
        "button:hover": {"background-color": "#3A7BC8"},
    }

```
```sh
hypie build -i ./app/CounterWidget.py -o ./app/static
```
(or your favourite backend)
```python
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

```