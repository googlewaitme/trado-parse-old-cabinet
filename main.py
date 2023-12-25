"""
created by bulat zaripov
04.12.2023
"""
import logging

import config
from db import DBConnector
from b24 import OrderFactory

from mytradoclub.auth_script import auth
from mytradoclub.parse_orders import parse_orders_by_session
from mytradoclub.parse_orders import parse_contacts


def upload_orders(session, db, last_uploaded_id, orders):
    order_factory = OrderFactory(config.B24_API_TOKEN)
    for order in orders:
        parse_contacts(session, order)
        order_factory.create_order(order)
        last_uploaded_id = max(last_uploaded_id, order.order_id)
        logging.info(f"last uploaded id {last_uploaded_id}")
        db.save("LAST_UPLOADED_ID", str(last_uploaded_id))


def main():
    session = auth()

    db = DBConnector(
        config.DB_HOST, config.DB_NAME, config.DB_USER, config.DB_PASSWORD
    )
    last_uploaded_id = 1
    if db.is_exists("LAST_UPLOADED_ID"):
        last_uploaded_id = int(db.get("LAST_UPLOADED_ID"))

    orders = parse_orders_by_session(session)
    orders.sort(key=lambda x: x.order_id)
    filtered_orders = [
        order for order in orders if order.order_id > last_uploaded_id
    ]
    logging.info(f"geeted LAST_UPLOADED_ID {last_uploaded_id}")
    logging.info("orders: " + str([el.order_id for el in filtered_orders]))
    upload_orders(session, db, last_uploaded_id, filtered_orders)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
