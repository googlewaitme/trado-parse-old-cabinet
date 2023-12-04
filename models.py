from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Contacts:
    delivery_address: Optional[str] = "empty address"
    phone: Optional[str] = "88001112233"
    email: Optional[str] = "empty@tradoclub.ru"


@dataclass
class Position:
    name: str = "tovar"
    count: int = 1
    id_bitrix: Optional[int] = None


@dataclass
class Order:
    order_id: int
    created: datetime
    author: str
    lastname: str
    name: str
    mname: Optional[str]
    positions: list[Position]
    delivery_type: str
    comment: Optional[str]
    contacts: Optional[Contacts] = None
