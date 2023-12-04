"""
created by bulat zaripov
04.12.2023
"""
import pickle
from datetime import datetime

import requests
from bs4 import BeautifulSoup

from models import Order, Contacts, Position
import config


def parse_contacts(page: BeautifulSoup) -> Contacts:
    delivery_address = parse_field(
        page, "edit-field-zakaz-delivery-address-0-value"
    )
    phone = parse_field(page, "edit-field-zakaz-phone-0-value")
    email = parse_field(page, "edit-field-zakaz-email-0-email")
    return Contacts(delivery_address, phone, email)


def parse_field(page: BeautifulSoup, tag_id: str) -> str:
    return get_object(page, tag_id).get("value")


def get_object(page: BeautifulSoup, tag_id: str) -> BeautifulSoup:
    return page.find("input", {"id": tag_id})


def parse_orders_list(page: BeautifulSoup) -> Order:
    content = page.find("div", {"class": "inner content"})
    table = content.find("tbody")
    rows = table.findAll("tr")
    orders = []
    for row in rows:
        order = get_order_from_row(row)
        orders.append(order)
    return orders


def get_order_from_row(row: BeautifulSoup) -> Order:
    splited = row.findAll("td")
    positions = create_positions_from_row(splited)
    order = Order(
        splited[0].string.strip(),
        datetime.strptime(splited[1].string.strip(), "%d-%m-%Y %H:%M"),
        splited[2].string.strip(),
        splited[3].string.strip(),
        splited[4].string.strip(),
        splited[5].string.strip(),
        positions,
        splited[9].string.strip(),
        splited[10].string.strip(),
    )
    #  for parsing contacts
    #  url splited[11].find("a").get("href")
    return order


def create_positions_from_row(splited: list[BeautifulSoup]) -> list[Position]:
    pos_names = [el.string.strip() for el in splited[6].findAll("div")]
    pos_counts = [el.string.strip() for el in splited[7].findAll("div")]
    positions = [Position(*el) for el in zip(pos_names, pos_counts)]
    if len(positions) == 0:
        positions.append(Position(
            splited[6].string.strip(),
            splited[7].string.strip()
        ))
    return positions


def main():
    session = requests.session()

    with open('session.cookies', 'rb') as f:
        session.cookies.update(pickle.load(f))
        print('session uploaded')

    parsedata = session.get(config.BASE_URL + "/zalazlist")

    page = BeautifulSoup(parsedata.text, "html.parser")

    orders = parse_orders_list(page)
    print(orders)

    parse_data = session.get(config.BASE_URL + "/node/24452709/edit")
    page = BeautifulSoup(parse_data.text, "html.parser")
    print(parse_contacts(page))


if __name__ == "__main__":
    main()
