from typing import Literal
from hypie.events import Event


class DeleteCartItem(Event):
    item_id: int


class ChangeCartItemQty(Event):
    item_id: int
    change: Literal["inc", "dec"]
