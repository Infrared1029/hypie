from typing import Literal

from hypie.events import Event


class CartItemsUpdatedEvent(Event):
    cart_items: list[dict]
    item_added: bool = False
