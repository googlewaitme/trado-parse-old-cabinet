"""
file created by googlewaitme
"""
import pickle
import requests
from bs4 import BeautifulSoup
import config


def create_session():
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


if __name__ == "__main__":
    create_session()
