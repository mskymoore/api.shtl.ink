# shtl.ink api
**URL Shortener built with Python and FastAPI**

## Read API Docs

1. Run App
2. Navigate to http://localhost:8000/docs or http://localhost:8000/redoc

## Build Local
```console
pip install -r requirements.txt
python -m build
```

## Run Local

```console
pip install shtl-ink-api
uvicorn shtl_ink.shtl_ink_api.app:app
```

## Build Docker
```console
docker build -t skymoore/shtl-ink-api .
```

## Run Docker

```console
docker pull skymoore/shtl-ink-api
docker run --rm -it  -p 8000:8000/tcp skymoore/shtl-ink-api:latest
```
