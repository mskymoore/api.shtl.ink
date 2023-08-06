import os

_app_name = "APP_NAME"
_base_url = "BASE_URL"
_frontend_base_url = "FRONTEND_BASE_URL"
_cookie_domain = "COOKIE_DOMAIN"
_db_host = "DB_HOST"
_db_name = "DB_NAME"
_db_user = "DB_USER"
_db_pass = "DB_PASS"

if _app_name in os.environ:
    app_name = os.environ[_app_name]
else:
    app_name = "shtl.ink"

if (
    _base_url in os.environ
    and _frontend_base_url in os.environ
    and _cookie_domain in os.environ
):
    base_url = os.environ[_base_url]
    frontend_base_url = os.environ[_frontend_base_url]
    cookie_domain = os.environ[_cookie_domain]
else:
    base_url = "http://localapi.shtl.ink:8000"
    frontend_base_url = "http://shtl.ink:3000"
    cookie_domain = ".shtl.ink"
    print("URL environment variables not set, falling back to demo mode")

if (
    _db_host in os.environ
    and _db_name in os.environ
    and _db_user in os.environ
    and _db_pass in os.environ
):
    db_host = os.environ[_db_host]
    db_name = os.environ[_db_name]
    db_user = os.environ[_db_user]
    db_pass = os.environ[_db_pass]
else:
    db_host, db_name, db_user, db_pass = None, None, None, None
    print("DB environment variables not set, falling back to sqlite")
