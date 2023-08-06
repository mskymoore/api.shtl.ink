import os
from logging import getLogger
from requests import post

log = getLogger(__name__)

_app_name = "APP_NAME"
_base_url = "BASE_URL"
_frontend_base_url = "FRONTEND_BASE_URL"
_cookie_domain = "COOKIE_DOMAIN"

_oidc_audience = "OIDC_AUDIENCE"
_oidc_issuer = "OIDC_ISSUER"
_client_id = "CLIENT_ID"
_client_secret = "CLIENT_SECRET"

_db_host = "DB_HOST"
_db_name = "DB_NAME"
_db_user = "DB_USER"
_db_pass = "DB_PASS"

app_name = os.environ.get(_app_name, "shtl.ink")
base_url = os.environ.get(_base_url, "http://localapi.shtl.ink:8000")
frontend_base_url = os.environ.get(_frontend_base_url, "http://shtl.ink:3000")
cookie_domain = os.environ.get(_cookie_domain, ".shtl.ink")

log.info(
    f"Initialized Config:\n\tapp_name: {app_name}\n\tbase_url: {base_url}\n\tfrontend_base_url: {frontend_base_url}\n\tcookie_domain: {cookie_domain}"
)

oidc_audience = os.environ.get(_oidc_audience, "api.shtl.ink")
oidc_issuer = os.environ.get(_oidc_issuer, "https://iam.rwx.dev/realms/rwxdev")
client_id = os.environ.get(_client_id, "api.shtl.ink")
client_secret = os.environ.get(_client_secret, None)

token_url = f"{oidc_issuer}/protocol/openid-connect/token"

token_response = post(
    token_url,
    data={
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
    },
    timeout=5,
)

if token_response.status_code == 200:
    token_data = token_response.json()
    access_token = token_data["access_token"]
    log.info(f"Access token obtained: {access_token}")
else:
    log.info(f"Failed to obtain token: {token_response.text}")


db_host = os.environ.get(_db_host, None)
db_name = os.environ.get(_db_name, None)
db_user = os.environ.get(_db_user, None)
db_pass = os.environ.get(_db_pass, None)

if db_host is None:
    log.info("DB environment variables not set, falling back to sqlite")
