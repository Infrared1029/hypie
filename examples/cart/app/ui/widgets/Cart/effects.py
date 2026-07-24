import hypie as hp
from ...hub.events import CartItemsUpdatedEvent
from ...hub.cart_store import store_query
from hypie.dom_position import closest
from .components.CartItems.CartItems import CartItems, AddedCartItem
from .components.Receipt.Receipt import RecieptClient


@hp.behavior
def rerender_cart_items():
    cart_items_q = hp.q(f"[{CartItems.cart_items_attr()}]").first()
    last_added_item_q = hp.q(f"[{AddedCartItem.add_cart_item_attr()}]").last()
    return hp.hs(
        hp.On(CartItemsUpdatedEvent.with_spec(from_=closest(store_query)))[
            hp.render(CartItems(CartItemsUpdatedEvent.cart_items)),
            hp.morph(cart_items_q, to=hp.result),
            hp.if_(CartItemsUpdatedEvent.item_added)[
                hp.scroll_to(last_added_item_q, "bottom", transition="smoothly")
            ],
        ],
    )


@hp.behavior
def rerender_reciept():
    return hp.hs(
        hp.On(CartItemsUpdatedEvent.with_spec(from_=closest(store_query)))[
            hp.js(CartItemsUpdatedEvent.cart_items)[
                """//js
                return CartItemsUpdatedEvent__cart_items.reduce((acc, i) => acc + (i["price"] * i["qty"]), 0).toFixed(2)
                """
            ],
            hp.render(RecieptClient(total=hp.result)),
            hp.morph(RecieptClient.receipt_query(), to=hp.result),
        ],
    )
