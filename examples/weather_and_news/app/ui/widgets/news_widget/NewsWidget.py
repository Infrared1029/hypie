from typing import TypedDict

import htpy
import hypie as hp

from .effects import rerender_news_widget


class News(TypedDict):
    text: str
    time: str


class NewsWidget(hp.ServerComponent):
    news: list[News]
    name: str

    def template(self):
        return htpy.div(
            _=hp.Install(rerender_news_widget),
            class_="relative flex flex-col gap-2 items-start w-sm p-3 border border-gray-200 rounded-sm",
            data_news_widget=True,
        )[
            htpy.h1["News"],
            htpy.div(class_="flex flex-col gap-2")[
                [
                    htpy.fragment[
                        htpy.p[n["text"]],
                        htpy.p(class_="text-xs")[f"{n['time']} ago"],
                    ]
                    for n in self.news
                ]
            ],
            htpy.p(class_="text-xs font-thin")[self.name],
            htpy.div(
                class_="hidden absolute w-full h-full top-0 left-0 bg-white/50",
                data_news_loading=True,
            ),
        ]
