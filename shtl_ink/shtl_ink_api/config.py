import os
from logging import getLogger

log = getLogger(__name__)

_app_name = "APP_NAME"
_base_url = "BASE_URL"
_frontend_base_url = "FRONTEND_BASE_URL"
_cookie_domain = "COOKIE_DOMAIN"

_db_host = "DB_HOST"
_db_name = "DB_NAME"
_db_user = "DB_USER"
_db_pass = "DB_PASS"

_oidc_audience = "OIDC_AUDIENCE"
_oidc_issuer = "OIDC_ISSUER"
_client_id = "CLIENT_ID"
_client_secret = "CLIENT_SECRET"

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

if client_secret is None:
    raise Exception("OIDC client secret not set")

db_host = os.environ.get(_db_host, None)
db_name = os.environ.get(_db_name, None)
db_user = os.environ.get(_db_user, None)
db_pass = os.environ.get(_db_pass, None)

if db_host is None:
    log.info("DB environment variables not set, falling back to sqlite")
