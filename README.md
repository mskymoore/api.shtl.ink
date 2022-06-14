# shtl.ink api
**URL Shortener built with Python and FastAPI**

[github repository](https://github.com/mskymoore/url_shortener)

## Read API Docs

1. Run App
2. Navigate to http://localhost:8000/docs or http://localhost:8000/redoc

## Configure environment variables
```
# requires postgres database
export BASE_URL=http://localhost:8000
# where to redirect / to
export ROOT_REDIRECT_URL=http://shtl.ink
export DB_HOST=abcd
export DB_NAME=abcd
export DB_USER=abcd
export DB_PASS=abcd
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

