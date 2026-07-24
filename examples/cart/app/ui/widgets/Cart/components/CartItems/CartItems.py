import htpy
import hypie as hp
from hypie.experimental.client_component import For
from .events import *


class AddedCartItem(hp.ClientComponent):
    item_id: int
    item_name: str
    item_price: float
    img_url: str
    qty: int = 1

    def template(self):
        return htpy.div(class_="flex justify-between min-w-0 p-1", data_cart_item=True)[
            htpy.div(class_="flex gap-2 min-w-0")[
                htpy.img(src=self.img_url, class_="w-[50px] h-[50px] shrink-0"),
                htpy.div(class_="flex flex-col min-w-0")[
                    htpy.p(class_="truncate")[self.item_name],
                    htpy.p[f"${self.item_price} each"],
                ],
            ],
            htpy.div(class_="flex gap-4 items-center w-2xs justify-end")[
                htpy.button(
                    class_="cursor-pointer",
                    _=hp.On("click")[
                        hp.trigger(ChangeCartItemQty(self.item_id, "dec"))
                    ],
                )["-"],
                htpy.p(class_="tabular-nums w-6 text-center")[self.qty],
                htpy.button(
                    class_="cursor-pointer",
                    _=hp.On("click")[
                        hp.trigger(ChangeCartItemQty(self.item_id, "inc"))
                    ],
                )["+"],
                htpy.p(id=f"item-total-price", class_="tabular-nums w-16 text-right")[
                    self.item_price * self.qty
                ],
                htpy.button(
                    class_="cursor-pointer text-red-300",
                    _=hp.On("click")[hp.trigger(DeleteCartItem(item_id=self.item_id))],
                )["Delete"],
            ],
        ]

    @classmethod
    def add_cart_item_attr(cls):
        return "data-cart-item"


class CartItems(hp.ClientComponent):
    items: list[dict]

    def template(self):
        item = hp.var("item")
        return htpy.div(
            class_="flex flex-col w-md gap-4 p-1 h-96 overflow-y-auto min-h-0  ",
            data_cart_items=True,
        )[
            For(item, self.items)[
                AddedCartItem(
                    item["id"],
                    item["name"],
                    item["price"],
                    item["img_url"],
                    item["qty"],
                )
            ]
        ]

    @classmethod
    def cart_items_attr(cls):
        return "data-cart-items"


class CartItemsSkeleton(hp.ServerComponent):
    def template(self):
        return htpy.div(
            class_="flex flex-col w-md gap-4 p-1 h-96 overflow-y-auto min-h-0 min-w-0 grow-0",
            data_cart_items=True,
        )

    @classmethod
    def cart_items_attr(cls):
        return "data-cart-items"
