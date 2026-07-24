import htpy
import hypie as hp

from ..widgets.regions_widget.RegionsWidget import RegionsWidget
from ..widgets.weather_widget.WeatherWidget import WeatherWidget
from ..widgets.weather_widget.effects import rerender_weather_widget
from ..widgets.news_widget.NewsWidget import NewsWidget
from ..widgets.news_widget.effects import rerender_news_widget
from ..hub.weather_news_hub import (
    weather_and_news_effects,
    weather_and_news_effects_streamed,
)


class WeatherAndNewsPage(hp.ServerComponent):
    weather_data: dict
    news_data: dict

    def template(self):
        return htpy.html[
            htpy.head[
                htpy.title["Weather and News"],
                htpy.link(rel="stylesheet", href="/static/tw_styles.css"),
                htpy.script(
                    type="text/hyperscript", src="/static/_hypie_hyperscript._hs"
                ),
                htpy.script(src="https://cdn.jsdelivr.net/npm/hyperscript.org@0.9.93"),
                htpy.script(
                    src="https://cdn.jsdelivr.net/npm/hyperscript.org@0.9.93/dist/ext/eventsource.min.js"
                ),
            ],
            htpy.title["Weather and News Demo"],
            htpy.body(
                # _=hp.Install(weather_and_news_effects),
                class_="w-screen h-screen flex flex-col items-start justify-start p-4 gap-4",
            )[
                htpy.div(
                    _=hp.Install(weather_and_news_effects),
                    class_="w-full flex flex-col items-start justify-start p-4 gap-4",
                )[
                    htpy.h1["SSR"],
                    RegionsWidget(),
                    htpy.div(class_="flex gap-2")[
                        WeatherWidget(**self.weather_data),
                        NewsWidget(**self.news_data),
                    ],
                ],
                htpy.div(
                    _=hp.Install(weather_and_news_effects_streamed),
                    class_="w-full flex flex-col items-start justify-start p-4 gap-4",
                )[
                    htpy.h1["Streamed SSR"],
                    RegionsWidget(),
                    htpy.div(class_="flex gap-2")[
                        WeatherWidget(**self.weather_data), NewsWidget(**self.news_data)
                    ],
                ],
            ],
        ]
