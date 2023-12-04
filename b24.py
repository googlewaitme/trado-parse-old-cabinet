'''
export orders from old site to bitrix24
'''
from bitrix24 import Bitrix24
from models import Order


class OrderFactory:
    def __init__(self, webhook_url: str):
        self.bx24 = Bitrix24(webhook_url)
        self.deal_id = 1

    def create_order(self, getted_order: Order):
        self.order = getted_order
        self.deal_id = self.bx24.callMethod(
            "crm.deal.add",
            fields={
                "TITLE": f"Старый ЛК {self.order.order_id}",
                "TYPE_ID": "GOODS",
                "STAGE_ID": "NEW",
                "OPENED": "Y",
                "CURRENCY_ID": "RUB",
                "BEGINDATE": self.order.created.strftime("%Y-%m-%d %H:%M:%S"),
            }
        )
        self._add_contacts()
        self._add_positions()

    def _add_contacts(self):
        pass

    def _add_positions(self):
        '''
        {
            0: {"PRODUCT_ID": 126, "QUANTITY": 2},
            1: {"PRODUCT_ID": 140, "QUANTITY": 1},
        },
        '''
        self._create_link_between_name_and_catalog()
        products = dict()
        for index, position in enumerate(self.order.positions):
            products[index] = {
                "PRODUCT_ID": position.id_bitrix,
                "QUANTITY": position.count
            }

        self.bx24.callMethod(
            "crm.deal.productrows.set",
            id=self.deal_id,
            rows=products
        )

    def _create_link_between_name_and_catalog(self):
        product_list = self.bx24.callMethod('crm.product.list')

        for el in product_list:
            print(el['NAME'])

    def get_product_fields(self) -> list[dict]:
        data = self.bx24.callMethod(
            "crm.productrow.fields"
        )
        return data
