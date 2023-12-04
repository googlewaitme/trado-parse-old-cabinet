"config file created by bulat"
from environs import Env

env = Env()

env.read_env()

DB_HOST = env("db_host")
DB_NAME = env("db_name")
DB_USER = env("db_user")
DB_PASSWORD = env("db_password")

BASE_URL = env("base_url_for_parsing")

SITE_AUTH_NAME = env("site_auth_name")
SITE_AUTH_PASSWORD = env("site_auth_password")
SITE_AUTH_OP = env("site_auth_op")

B24_API_TOKEN = env("bitrix_24_api_url")
