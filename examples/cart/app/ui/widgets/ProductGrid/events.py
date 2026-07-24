from hypie.events import Event


class AddProductToCartEvent(Event):
    id: int
    name: str
    price: float
    img_url: str
