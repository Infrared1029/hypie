import htpy
import hypie as hp

from .events import *


class Product(hp.ServerComponent):
    id: int
    title: str
    price: float
    image_url: str

    def template(self):
        s = hp.On("click")[
            hp.trigger(
                AddProductToCartEvent(self.id, self.title, self.price, self.image_url)
            ),
        ]
        # print(s.render())
        return htpy.div(
            class_="cursor-pointer select-none flex flex-col gap-1 justify-center items-center",
            data_product_id=self.id,
            _=s,
        )[
            htpy.img(class_="w-[200px]", src=self.image_url),
            htpy.h1[self.title],
            htpy.h3[str(self.price)],
        ]


class ProductGrid(hp.ServerComponent):
    products: list[Product]

    def template(self):
        return htpy.div(class_="grid grid-cols-3 gap-2 overflow-y-auto min-h-0 p-2")[
            self.products
        ]
