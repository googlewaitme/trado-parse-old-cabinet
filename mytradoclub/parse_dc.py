from mytradoclub.models import Distributor
from bs4 import BeautifulSoup, PageElement
import config
from typing import Optional
import pickle


URL = config.BASE_URL + "/mlm2/rdcreport"
TEMPLATE_URL = config.BASE_URL + "/mlm2/rdcreport?period_nid={}"


def parse_dc_from_row(row: PageElement) -> Optional[Distributor]:
    splitted = row.findAll("td")
    dist = Distributor()
    if splitted[2] is not None:
        dist.fio = splitted[2].string.strip()
    if splitted[3].find("a") is not None:
        dist.club_number = splitted[3].find("a").text.strip()
    return dist if dist.club_number is not None else None


def parse_dc_on_page(session, url) -> list[Distributor]:
    parse_data = session.get(url)
    page = BeautifulSoup(parse_data.text, "html.parser")
    content = page.find("div", {"class": "inner content"})
    table = content.find("tbody")
    rows = table.findAll("tr")
    distributors = []
    for row in rows:
        distributor = parse_dc_from_row(row)
        if distributor is not None:
            distributors.append(distributor)
    return distributors


def parse_dc_by_session(session) -> list[Distributor]:
    parse_data = session.get(URL)
    page = BeautifulSoup(parse_data.text, "html.parser")
    select = page.find("select")
    options = select.findAll("option")
    distributors = []
    for option in options[:12]:
        period_nid = option.get("value")
        url_to_parse = TEMPLATE_URL.format(period_nid)
        distributors += parse_dc_on_page(session, url_to_parse)
    return distributors


def dumps_dc(distributors: list[Distributor], filename: str) -> None:
    with open(filename, "wb") as f:
        pickle.dump(distributors, f)


def loads_dc(filename) -> list[Distributor]:
    with open(filename, 'rb') as f:
        distributors = pickle.load(f)
    return distributors
