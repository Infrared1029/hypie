import htpy
import hypie as hp

from .effects import rerender_weather_widget


class WeatherWidget(hp.ServerComponent):
    temp: int
    high: int
    low: int
    condition: str
    name: str

    def template(self):
        return htpy.div(
            _=hp.Install(rerender_weather_widget),
            class_="relative flex flex-col gap-2 items-start w-sm p-3 border border-gray-200 rounded-sm",
            data_weather_widget=True,
        )[
            htpy.h1["Weather"],
            htpy.div(class_="flex flex-col")[
                htpy.p(class_="text-lg font-bold")[self.temp],
                htpy.p[self.condition],
            ],
            htpy.p[f"High {self.high} . {self.low}"],
            htpy.p(class_="text-xs font-thin")[self.name],
            htpy.div(
                class_="hidden absolute w-full h-full top-0 left-0 bg-white/50",
                data_weather_loading=True,
            ),
        ]
