import htpy
import hypie as hp

# from ...store.store import CartStore
from .components.CartItems.CartItems import CartItemsSkeleton
from .components.Receipt.Receipt import Receipt
from .effects import rerender_cart_items, rerender_reciept


class Cart(hp.ServerComponent):
    def template(self):
        return htpy.div(
            _=hp.Install(rerender_cart_items, rerender_reciept),
            class_="flex flex-col gap-3 w-lg justify-center items-center",
        )[CartItemsSkeleton, Receipt()]
