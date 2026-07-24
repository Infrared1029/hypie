from typing import Annotated

import hypie as hp
from hypie.events import Event

from ..widgets.regions_widget.events import *


class UpdateWeatherNewEvent(Event):
    dom_patch: Annotated[str, "HTML"]


class RequestingRegionDataEvent(Event):
    pass


@hp.behavior
def weather_and_news_effects():
    return hp.hs(
        hp.Init(immediately=True)[hp.set_(hp.attr("data-weather-news-hub"), to=True)],
        hp.On(RegionClicked)[
            hp.trigger(RequestingRegionDataEvent),
            hp.fetch(f"/data?region_id={RegionClicked.region}", as_="HTML"),
            hp.trigger(UpdateWeatherNewEvent(dom_patch=hp.result)),
        ],
    )


@hp.behavior
def weather_and_news_effects_streamed():
    return hp.hs(
        hp.Init(immediately=True)[hp.set_(hp.attr("data-weather-news-hub"), to=True)],
        hp.On(RegionClicked)[
            hp.trigger(RequestingRegionDataEvent),
            hp.fetch(f"/stream/data?region_id={RegionClicked.region}", as_="Stream"),
        ],
        hp.On("server:fragment")[
            hp.trigger(
                UpdateWeatherNewEvent(
                    dom_patch=hp.as_type(hp.var("event").detail.data, "Fragment")
                )
            )
        ],
    )
