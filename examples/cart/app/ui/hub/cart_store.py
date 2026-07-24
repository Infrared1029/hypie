import hypie as hp

from .events import *
from ..widgets.ProductGrid.events import AddProductToCartEvent
from ..widgets.Cart.components.CartItems.events import *


store = hp.var("^store")
store_query = hp.q("[data-cart-store]")


@hp.behavior
def cart_store_setup():
    return hp.hs(
        hp.Init(immediately=True)[
            # mark owner as the store
            hp.set_(hp.attr("data-cart-store"), to=True),
            # set state
            hp.set_(store, to={"items": []}),
        ],
        # handle events
        hp.On(AddProductToCartEvent)[
            hp.set_(hp.var("my_store"), to=hp.var("^store")),
            hp.js(
                "my_store",
                AddProductToCartEvent.id,
                AddProductToCartEvent.name,
                AddProductToCartEvent.price,
                AddProductToCartEvent.img_url,
            )[
                """//js
                const id = AddProductToCartEvent__id;
                const exists = my_store.items.some(p => p.id === id);
                const newItems = exists
                ? my_store.items.map(p => p.id === id ? { ...p, qty: p.qty + 1 } : p)
                : [...my_store.items, {
                    id,
                    name: AddProductToCartEvent__name,
                    price: AddProductToCartEvent__price,
                    img_url: AddProductToCartEvent__img_url,
                    qty: 1
                    }];
                return { items: newItems, item_added: !exists };
                """
            ],
            hp.set_(store, to={"items": hp.result["items"]}),
            hp.trigger(
                CartItemsUpdatedEvent(
                    hp.result["items"], item_added=hp.result["item_added"]
                )
            ),
        ],
        hp.On(DeleteCartItem)[
            hp.set_(hp.var("my_store"), to=hp.var("^store")),
            hp.js("my_store", DeleteCartItem.item_id)[
                """//js
                let items = my_store['items'].filter(i => i["id"] !== DeleteCartItem__item_id)
                return {"items": items}
                """
            ],
            hp.set_(store, hp.result),
            hp.trigger(CartItemsUpdatedEvent(store["items"])),
        ],
        hp.On(ChangeCartItemQty)[
            hp.set_(hp.var("my_store"), to=hp.var("^store")),
            hp.js("my_store", ChangeCartItemQty.item_id, ChangeCartItemQty.change)[
                """//js
                let items = my_store['items'].map(i => i["id"] == ChangeCartItemQty__item_id 
                    ? (ChangeCartItemQty__change == "inc" 
                    ? {...i, "qty": i["qty"] + 1} 
                    : {...i, "qty": i["qty"] - 1}) : {...i}
                )
                items = items.filter(i => i["qty"] !== 0)
                return {"items": items}
                """
            ],
            hp.set_(store, hp.result),
            hp.trigger(CartItemsUpdatedEvent(store["items"])),
        ],
    )
