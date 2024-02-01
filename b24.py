'''
export orders from old site to bitrix24
'''
import logging
from typing import Optional

import Levenshtein
from bitrix24 import Bitrix24

from models import Order


def create_link_between_name_and_catalog(order, product_list):
    """
    product_list = list[dict["TO_SEARCH", "NAME", "ID", "PRICE"]]
    keys: "TO_SEARCH" = prepare_string("NAME")
    "NAME" - from catalog
    "ID" - catalog bitrix_id
    "PRICE" - catalog price
    """
    for position in order.positions:
        min_dist = len(position.name) * 2
        to_search_name = prepare_string(position.name)
        for product in product_list:
            current_dist = Levenshtein.distance(
                to_search_name, product['TO_SEARCH']
            )
            if current_dist < min_dist:
                min_dist = current_dist
                position.name = product["NAME"]
                position.id_bitrix = product["ID"]
                position.price = product["PRICE"]


def prepare_string(st):
    "prepare string for Levenshtein algorithm"
    return "".join(sorted(st.lower().split()))


class OrderFactory:
    def __init__(self, webhook_url: str):
        self.bx24 = Bitrix24(webhook_url)
        self.set_product_list()

    def set_product_list(self) -> None:
        self.product_list = self.bx24.callMethod('crm.product.list')
        for el in self.product_list:
            el["TO_SEARCH"] = prepare_string(el["NAME"])

    def create_order(self, getted_order: Order):
        self.order = getted_order
        self._set_comment()
        self.deal_id = self.bx24.callMethod(
            "crm.deal.add",
            fields={
                "TITLE": f"old lk {self.order.order_id}",
                "TYPE_ID": "GOODS",
                "STAGE_ID": "NEW",
                "OPENED": "Y",
                "CURRENCY_ID": "RUB",
                "BEGINDATE": self.order.created.strftime("%Y-%m-%d %H:%M:%S"),
                "COMMENTS": self.comment,
                "UF_CRM_1706778766269": self.technical_comment,
                "UF_CRM_1706782366394": self.order.contacts.delivery_address,
                "UF_CRM_1706782377221": self.order.delivery_type
            }
        )
        self._add_contacts()
        self._add_positions()

    def _set_comment(self):
        self.comment = self.order.comment
        self.technical_comment = str(self.order)

    def _add_contacts(self):
        if not self._contacts_is_exists():
            self._create_contacts()
        self.bx24.callMethod(
            "crm.deal.contact.add",
            id=self.deal_id,
            fields={
                "CONTACT_ID": self.contact_id
            }
        )

    def _contacts_is_exists(self) -> bool:
        self.contact_id = self._get_contact_id()
        return self.contact_id is not None

    def _get_contact_id(self) -> Optional[int]:
        if len(self.order.contacts.phone) > 0:
            to_search_phone = self._normalize_phone(self.order.contacts.phone)
            logging.info("search phone " + to_search_phone)
            contact = self._crm_contact_list_get({"PHONE": to_search_phone})
            if contact:
                return contact['ID']
        if len(self.order.contacts.email) > 0:
            to_search_email = self.order.contacts.email
            logging.info("search email " + to_search_email)
            contact = self._crm_contact_list_get({"EMAIL": to_search_email})
            if contact:
                return contact["ID"]

    def _crm_contact_list_get(self, filter: dict):
        result = self.bx24.callMethod(
            "crm.contact.list",
            filter=filter,
            select=["*"]
        )
        if result:
            if len(result) == 1:
                return result[0]

    def _normalize_phone(self, phone: str) -> str:
        phone = phone.replace(" ", "").replace("+", '').replace("-", '')
        phone = phone.replace("(", "").replace(")", "")
        return phone[-10:]

    def _create_contacts(self) -> None:
        contact = self.bx24.callMethod('crm.contact.add', fields={
            "NAME": self.order.name,
            "SECOND_NAME": self.order.mname,
            "LAST_NAME": self.order.lastname,
            "TYPE_ID": "CLIENT",
            "PHONE": [{
                "VALUE": self.order.contacts.phone,
                "VALUE_TYPE": "WORK"
            }],
            "EMAIL": [{"VALUE": self.order.contacts.email}]
        })
        self.contact_id = int(contact)

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
                "QUANTITY": position.count,
                "PRICE": position.price
            }

        self.bx24.callMethod(
            "crm.deal.productrows.set",
            id=self.deal_id,
            rows=products
        )

    def _create_link_between_name_and_catalog(self):
        create_link_between_name_and_catalog(self.order, self.product_list)

    def get_product_fields(self) -> list[dict]:
        data = self.bx24.callMethod("crm.productrow.fields")
        return data

    def get_contact_fields(self) -> list[dict]:
        data = self.bx24.callMethod("crm.contact.fields")
        return data

    def get_deal_fields(self) -> list[dict]:
        data = self.bx24.callMethod("crm.deal.fields")
        return data
