import logging
import requests
import pickle
from bs4 import BeautifulSoup
import os

import config


def create_session() -> requests.Session:
    """creates session file"""
    session = requests.session()

    auth_page = session.get(config.BASE_URL)
    soup = BeautifulSoup(auth_page.text, "html.parser")

    form_id_tag = soup.find("input", {"name": "form_id"})
    form_id = form_id_tag.get("value")
    form_build_id_obj = soup.find("input", {"name": "form_build_id"})
    form_build_id = form_build_id_obj.get("value")

    authdata = {
        "name": config.SITE_AUTH_NAME,
        "pass": config.SITE_AUTH_PASSWORD,
        "op": config.SITE_AUTH_OP,
        "form_build_id": form_build_id,
        "form_id": form_id
    }
    session.post(config.BASE_URL + "/distrmain", data=authdata)

    with open('session.cookies', 'wb') as f:
        pickle.dump(session.cookies, f)
        print('session created')
    return session


def check_session_cookies() -> None:
    if os.path.isfile(config.COOKIES_PATH):
        return
    create_session()


def upload_session() -> requests.Session:
    session = requests.session()
    with open(config.COOKIES_PATH, 'rb') as f:
        session.cookies.update(pickle.load(f))
    return session


def is_old_session(session: requests.Session) -> bool:
    parsedata = session.get(config.BASE_URL + "/zalazlist")
    page = BeautifulSoup(parsedata.text, "html.parser")
    content = page.find("div", {"class": "inner content"})
    return content is None


def update_session():
    return create_session()


def auth() -> requests.Session:
    logging.info("auth mytradoclub")
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
    return session
