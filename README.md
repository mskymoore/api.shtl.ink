# shtl.ink api with keycloak oauth endpoint protection
**URL Shortener built with Python and FastAPI**

[github repository](https://github.com/mskymoore/url_shortener)

## Read API Docs

1. Run App
2. Navigate to http://localhost:8000/docs or http://localhost:8000/redoc

## Create a `.env` file
```
APP_NAME=shtl.ink
BASE_URL=http://localhost:8000
# where to redirect / to, also allow_origin
FRONTEND_BASE_URL=http://shtl.ink
COOKIE_DOMAIN=.shtl.ink

OIDC_AUDIENCE=api.shtl.ink
OIDC_ISSUER=iam.rwx.dev/realms/rwxdev

# optional to request a token with test.py
CLIENT_ID=someClientId
CLIENT_SECRET=someClientSecret
TEST_USER=username
TEST_PASS=password

# requires postgres database
DB_HOST=abcd
DB_NAME=abcd
DB_USER=abcd
DB_PASS=abcd
```

## Build Local
```console
pip install -r requirements.txt
python -m build
```
## Run Local

```console
pip install shtl-ink-api
uvicorn shtl_ink_api.app:app
```

## Docker Compose
  See docker-compose.yml

## Build Docker
```console
docker build -t skymoore/shtl-ink-api .
```

## Run Docker

```console
docker pull skymoore/shtl-ink-api
docker run --rm -it  -p 8000:8000/tcp skymoore/shtl-ink-api:latest
```

