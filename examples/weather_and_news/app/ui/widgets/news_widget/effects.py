import hypie as hp
from hypie.dom_position import closest
from ...hub.weather_news_hub import UpdateWeatherNewEvent, RequestingRegionDataEvent


@hp.behavior
def rerender_news_widget():
    return hp.hs(
        hp.On(
            RequestingRegionDataEvent.with_spec(
                from_=closest(hp.q("[data-weather-news-hub]"))
            )
        )[
            hp.remove(hp.cls("hidden"), from_=hp.q("[data-news-loading]").in_(hp.me)),
        ],
        hp.On(
            UpdateWeatherNewEvent.with_spec(
                from_=closest(hp.q("[data-weather-news-hub]"))
            )
        )[
            # hp.log("patch", UpdateWeatherNewEvent.dom_patch),
            hp.set_(
                hp.var("my_patch"),
                to=hp.q("[data-news-widget]")
                .in_(UpdateWeatherNewEvent.dom_patch)
                .first(),
            ),
            hp.if_(hp.var("my_patch"))[
                hp.morph(hp.me, to=hp.var("my_patch")),
                hp.add(hp.cls("hidden"), to=hp.q("[data-news-loading]").in_(hp.me)),
            ],
        ],
    )
