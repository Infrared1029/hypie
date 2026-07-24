import htpy
import hypie as hp


class Receipt(hp.ServerComponent):
    total: float = 0

    def template(self):
        return htpy.div(data_cart_receipt=True, class_="flex flex-col")[
            htpy.div(class_="flex justify-between gap-2")[
                htpy.p["Total"], htpy.p(id="receipt-total")[self.total]
            ],
        ]

    @classmethod
    def receipt_query(cls):
        return hp.q("[data-cart-receipt]")


class RecieptClient(hp.ClientComponent):
    total: float = 0

    def template(self):
        return htpy.div(data_cart_receipt=True, class_="flex flex-col")[
            htpy.div(class_="flex justify-between gap-2")[
                htpy.p["Total"], htpy.p(id="receipt-total")[self.total]
            ],
        ]

    @classmethod
    def receipt_query(cls):
        return hp.q("[data-cart-receipt]")
