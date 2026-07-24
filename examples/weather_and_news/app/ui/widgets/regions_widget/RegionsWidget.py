import htpy

import hypie as hp
from .events import *


class RegionsWidget(hp.ServerComponent):
    def template(self):
        return htpy.div(class_="flex flex-col gap-2")[
            htpy.h1(class_="text-3xl")["Regions"],
            htpy.div(class_="flex justify-start gap-2 items-center")[
                htpy.button(
                    _=hp.On("click")[hp.trigger(RegionClicked("tokyo"))],
                    class_="border border-black rounded-sm p-1 cursor-pointer",
                )["Tokyo, JP"],
                htpy.button(
                    _=hp.On("click")[hp.trigger(RegionClicked("lisbon"))],
                    class_="border border-black rounded-sm p-1 cursor-pointer",
                )["Lisbon, PT"],
            ],
        ]
