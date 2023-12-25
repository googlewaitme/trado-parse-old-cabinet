from mytradoclub.auth_script import auth
from mytradoclub import parse_orders
import b24
import config


def load_orders():
    print(parse_orders.load_orders("orders.data"))


def get_orders_from_backup():
    order_factory = b24.OrderFactory(config.B24_API_TOKEN)
    orders = parse_orders.load_orders("orders.data")
    parse_orders.add_prices_for_orders(order_factory, orders)
    return orders


def create_csv():
    orders = get_orders_from_backup()
    parse_orders.create_csv(orders, "orders.csv")


def create_csv_with_positions():
    orders = get_orders_from_backup()
    parse_orders.create_csv_with_positions(orders, "lk_orders_with_products.csv")


def main():
    session = auth()
    orders = parse_orders.parse_all_orders(session)
    parse_orders.dump_orders(orders, "orders.data")


if __name__ == "__main__":
    # main()
    # load_orders()
    # create_csv()
    create_csv_with_positions()
