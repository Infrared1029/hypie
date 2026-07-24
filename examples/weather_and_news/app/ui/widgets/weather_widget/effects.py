import hypie as hp
from hypie.dom_position import closest
from ...hub.weather_news_hub import UpdateWeatherNewEvent, RequestingRegionDataEvent


@hp.behavior
def rerender_weather_widget():
    return hp.hs(
        hp.On(
            RequestingRegionDataEvent.with_spec(
                from_=closest(hp.q("[data-weather-news-hub]"))
            )
        )[
            hp.remove(
                hp.cls("hidden"), from_=hp.q("[data-weather-loading]").in_(hp.me)
            ),
        ],
        hp.On(
            UpdateWeatherNewEvent.with_spec(
                from_=closest(hp.q("[data-weather-news-hub]"))
            )
        )[
            hp.set_(
                hp.var("my_patch"),
                to=hp.q("[data-weather-widget]")
                .in_(UpdateWeatherNewEvent.dom_patch)
                .first(),
            ),
            hp.if_(hp.var("my_patch"))[hp.morph(hp.me, to=hp.var("my_patch"))],
        ],
    )
