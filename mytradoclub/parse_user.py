import requests
import config
from bs4 import BeautifulSoup


URL = config.BASE_URL + "/users/"
TEMPLATE_URL = config.BASE_URL + "/users/{}"


def parse_by_club_number(session: requests.Session, club_number: str) -> str:
    url_to_parse = TEMPLATE_URL.format(club_number)
    parse_data = session.get(url_to_parse)
    page = BeautifulSoup(parse_data.text, "html.parser")
    email_field_block = page.find('div', {'class': "field-field-profile-email"})
    email = email_field_block.find("a")
    return email.string.strip()
