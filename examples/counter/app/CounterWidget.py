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
