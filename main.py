"""
created by bulat zaripov
04.12.2023
"""
import pickle
from datetime import datetime
import os
import logging

import requests
from bs4 import BeautifulSoup

from models import Order, Contacts, Position
import config
from create_session import create_session
from db import DBConnector
from b24 import OrderFactory


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
        order_id=splited[0].string.strip(),
        created=datetime.strptime(splited[1].string.strip(), "%d-%m-%Y %H:%M"),
        author=splited[2].string.strip(),
        lastname=splited[3].string.strip(),
        name=splited[4].string.strip(),
        mname=splited[5].string.strip(),
        positions=positions,
        delivery_type=splited[9].string.strip(),
        comment=splited[10].string.strip(),
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


def check_session_cookies() -> None:
    if os.path.isfile(config.COOKIES_PATH):
        return
    create_session()


def upload_session() -> requests.Session:
    session = requests.session()
    with open(config.COOKIES_PATH, 'rb') as f:
        session.cookies.update(pickle.load(f))
        print('session uploaded')
    return session


def is_old_session(session: requests.Session) -> bool:
    parsedata = session.get(config.BASE_URL + "/zalazlist")
    page = BeautifulSoup(parsedata.text, "html.parser")
    content = page.find("div", {"class": "inner content"})
    return content is not None


def update_session():
    return create_session()


def main():
    session: requests.Session
    check_session_cookies()
    if os.path.isfile(config.COOKIES_PATH):
        session = upload_session()
        logging.info("upload session")
    else:
        session = update_session()
        logging.info("create new session: not exists")
    if is_old_session(session):
        session = update_session()
        logging.info("create new session: old")
    parsedata = session.get(config.BASE_URL + "/zalazlist")

    page = BeautifulSoup(parsedata.text, "html.parser")

    db = DBConnector(
        config.DB_HOST, config.DB_NAME, config.DB_USER, config.DB_PASSWORD
    )
    last_uploaded_id = 1
    if db.is_exists("LAST_UPLOADED_ID"):
        last_uploaded_id = int(db.get("LAST_UPLOADED_ID"))
    else:
        db.save("LAST_UPLOADED_ID", str(last_uploaded_id))

    orders = parse_orders_list(page)
    # TODO filter orderds which ID > last_uploaded_id
    print(orders)
    for order in orders:
        # TODO add contacts here
        parse_data = session.get(config.BASE_URL + "/node/24452709/edit")
        page = BeautifulSoup(parse_data.text, "html.parser")
        print(parse_contacts(page))
        order_factory = OrderFactory(config.B24_API_TOKEN)
        order_factory.create_order(order)


if __name__ == "__main__":
    main()
