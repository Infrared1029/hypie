import htpy
from hypie.experimental.components import Component
from hypie.literals import var
from hypie.features import On
from hypie.commands import set_
from hypie import hs


class Counter(Component):
    initial_count: int = 0

    def template(self):
        count_var = var(":count")

        return htpy.div[
            htpy.button(
                _=hs(
                    set_(count_var, to=self.initial_count),
                    On("click")[
                        set_(count_var, to=count_var + 1),
                        set_(var("me").textContent, to=f"Count is: {count_var}"),
                    ],
                )
            )[f"Count is: {self.initial_count}"]
        ]

    @staticmethod
    def style():
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


class Layout(Component):
    def template(self):
        return htpy.html[
            htpy.head[
                htpy.title["Counter"],
                htpy.link(rel="stylesheet", href="/static/_hypie_styles.css"),
                # _hyperscript
                htpy.script(src="https://cdn.jsdelivr.net/npm/hyperscript.org@0.9.93"),
            ],
            htpy.body[self.children],
        ]
