from datetime import datetime
import requests
from models import Order, Contacts, Position
from bs4 import BeautifulSoup
import json
import logging
import config
import pickle
from mytradoclub.parse_dc import loads_dc
import b24
import csv


def dump_orders(distributors: list[Order], filename: str) -> None:
    with open(filename, "wb") as f:
        pickle.dump(distributors, f)


def load_orders(filename) -> list[Order]:
    with open(filename, 'rb') as f:
        distributors = pickle.load(f)
    return distributors


def create_csv_with_positions(orders: list[Order], filename: str) -> None:
    dc_clubs = [dc.club_number for dc in loads_dc("distibutors.data")]
    fields = ["id", "date", "user_id", "name", "count", "price", "is_dc"]
    csv_array = []
    for order in orders:
        csv_array.append([
            order.order_id,
            order.created,
            order.author,
            order.positions[0].name,
            order.positions[0].count,
            order.positions[0].price,
            # json.dumps(positions),
            1 if order.author in dc_clubs else 0
        ])
        for position in order.positions[1:]:
            csv_array.append([
                None,
                None,
                None,
                position.name,
                position.count,
                position.price,
                None
            ])

    with open(filename, "w") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(fields)
        writer.writerows(csv_array)


def create_csv(orders: list[Order], filename: str) -> None:
    dc_clubs = [dc.club_number for dc in loads_dc("distibutors.data")]
    csv_array = []
    fields = ["id", "date", "user_id", "qsku", "sku", "sum_cheque", "is_dc"]
    for order in orders:
        for pos in order.positions:
            if pos.price is None or pos.price == '':
                pos.price = 0
            if pos.count is None or pos.count == '':
                pos.count = 0
        csv_array.append([
            order.order_id,
            order.created,
            order.author,
            sum(int(el.count) for el in order.positions),
            len(order.positions),
            # order.positions,
            sum(float(pos.price)*float(pos.count) for pos in order.positions),
            1 if order.author in dc_clubs else 0
        ])
    with open(filename, "w") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(fields)
        writer.writerows(csv_array)


def add_prices_for_orders(bitrix: b24.OrderFactory, orders: list[Order]):
    catalog = bitrix.product_list
    for i in range(len(orders)):
        b24.create_link_between_name_and_catalog(orders[i], catalog)


def parse_all_orders(session, count_pages=18) -> list[Order]:
    orders = []
    for page in range(count_pages):
        url = config.BASE_URL + f"/zalazlist?page={page}"
        orders += parse_orders_by_url(session, url)
    return orders


def parse_orders_by_session(session) -> list[Order]:
    return parse_orders_by_url(config.BASE_URL + "/zalazlist")


def parse_orders_by_url(session, url) -> list[Order]:
    logging.info(f"parse {url}")
    parsedata = session.get(url)
    page = BeautifulSoup(parsedata.text, "html.parser")
    orders = parse_orders_list(page)
    return orders


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
        order_id=int(splited[0].string.strip()),
        created=datetime.strptime(splited[1].string.strip(), "%d-%m-%Y %H:%M"),
        author=splited[2].string.strip(),
        lastname=splited[3].string.strip(),
        name=splited[4].string.strip(),
        mname=splited[5].string.strip(),
        positions=positions,
        delivery_type=splited[9].string.strip(),
        comment=splited[10].string.strip(),
        contacts=Contacts(
            url=config.BASE_URL+splited[11].find("a").get("href")
        )
    )
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


def parse_contacts(session: requests.Session, order: Order) -> None:
    parse_data = session.get(order.contacts.url)
    page = BeautifulSoup(parse_data.text, "html.parser")

    order.contacts.delivery_address = parse_field(
        page, "edit-field-zakaz-delivery-address-0-value"
    )
    order.contacts.phone = parse_field(page, "edit-field-zakaz-phone-0-value")
    order.contacts.email = parse_field(page, "edit-field-zakaz-email-0-email")


def parse_field(page: BeautifulSoup, tag_id: str) -> str:
    return get_object(page, tag_id).get("value")


def get_object(page: BeautifulSoup, tag_id: str) -> BeautifulSoup:
    return page.find("input", {"id": tag_id})
