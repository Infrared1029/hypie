from typing import Literal

import htpy
import hypie as hp
from ..widgets.Cart.Cart import Cart
from ..widgets.Cart.components.CartItems.CartItems import CartItems
from ..widgets.Cart.components.Receipt.Receipt import RecieptClient
from ..widgets.ProductGrid.ProductGrid import ProductGrid, Product
from ..hub.cart_store import cart_store_setup


class CartApp(hp.ServerComponent):
    products: list[dict]

    def template(self):
        return htpy.html[
            htpy.head[
                htpy.title["Cart Example"],
                htpy.link(rel="stylesheet", href="/static/tw_styles.css"),
                htpy.script(
                    type="text/hyperscript", src="/static/_hypie_hyperscript._hs"
                ),
                CartItems.register_template(),
                RecieptClient.register_template(),
                htpy.script(src="https://cdn.jsdelivr.net/npm/hyperscript.org@0.9.93"),
            ],
            htpy.body(
                class_="w-screen h-screen flex justify-center gap-5 items-stretch min-h-0",
                _=hp.Install(cart_store_setup),
            )[
                # CartStore[
                ProductGrid(products=[Product(**p) for p in self.products]), Cart
                # ]
            ],
        ]
