'''
export orders from old site to bitrix24
'''
import datetime

from bitrix24 import Bitrix24
from models import Position, Order

import config


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


if __name__ == "__main__":
    order = Order(
        order_id='3153',
        created=datetime.datetime(2023, 11, 23, 16, 1),
        author='001-000000',
        name='Ivanov',
        lastname='Ivan',
        mname='Ivanovich',
        positions=[
            Position(name='ВА 02 МЕНКОР', count='1'),
            Position(name='ВА 16 РЕСПИБЛИСС СИРОП', count='1'),
            Position(name='ВА 22 ЛИВОБЛИСС', count='1'),
            Position(name='ВА 23 РЕСПИБЛИСС', count='1'),
            Position(name='ВА 38 ЭНЕРГОБЛИСС', count='1'),
            Position(name='ВА 47 ИММУНОБЛИСС', count='1'),
            Position(name='ВА 49 УРИГАРД', count='1')
        ],
        delivery_type='Доставка до пункта выдачи СДЭК',
        comment=''
    )
    order_factory = OrderFactory(config.B24_API_TOKEN)
    order_factory.create_order(order)
