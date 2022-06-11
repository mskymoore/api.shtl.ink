from fastapi import FastAPI, Depends, Request, Form, status

from starlette.responses import RedirectResponse, JSONResponse
from starlette.templating import Jinja2Templates

import json
from sqlalchemy import select, delete
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from src.models.short_url_model import ShortURLModel, Base
from src.codec.codec import Codec
from .database import SessionLocal, engine

Base.metadata.create_all(bind=engine)

templates = Jinja2Templates(directory="src/frontend/templates")
codec = Codec()
app = FastAPI()


# Dependency
def get_db():
    db = Session(engine)
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def home(request: Request, db: Session = Depends(get_db)):
    coded_urls = db.execute(select(ShortURLModel)).scalars().all()
    return templates.TemplateResponse(
        "base.html", {"request": request, "coded_urls": coded_urls})


@app.post("/add")
def add(request: Request, url: str = Form(...), db: Session = Depends(get_db)):
    url_record = db.execute(
        select(ShortURLModel).where(
            ShortURLModel.url == url)).scalars().first()

    if url_record is None:
        short_code = codec.encode(url, db)

    else:
        return JSONResponse(url_record.to_dict(),
                            status_code=status.HTTP_208_ALREADY_REPORTED)

    if isinstance(short_code, str):
        url_record = db.get(ShortURLModel, (short_code))
        return JSONResponse(
            url_record.to_dict(),
            status_code=status.HTTP_201_CREATED)
    else:
        return RedirectResponse(
            url=app.url_path_for("home"),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@app.get("/{short_code}")
def go_to_url(
        request: Request,
        short_code: str,
        db: Session = Depends(get_db)):

    url = codec.decode(short_code, db)
    if url is None:
        return RedirectResponse(
            url=app.url_path_for("home"),
            status_code=status.HTTP_404_NOT_FOUND)
    else:
        return RedirectResponse(
            url=url, status_code=status.HTTP_307_TEMPORARY_REDIRECT)


@app.get("/delete/{short_code}")
def url_delete(
        request: Request,
        short_code: str,
        db: Session = Depends(get_db)):
    try:
        db.execute(
            delete(ShortURLModel).where(
                ShortURLModel.short_code == short_code))
        db.commit()
        return RedirectResponse(
            url=app.url_path_for("home"),
            status_code=status.HTTP_200_OK)
    except Exception as e:
        db.rollback()
        print
        return RedirectResponse(
            url=app.url_path_for("home"),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@app.post("/modify/{short_code}")
def modify(
        request: Request,
        short_code: str,
        new_short_code: str = Form(...),
        db: Session = Depends(get_db)):
    url_record = db.get(ShortURLModel, (short_code))
    if url_record is None:
        return RedirectResponse(
            url=app.url_path_for("home"),
            status_code=status.HTTP_404_NOT_FOUND)
    else:
        try:
            url_record.short_code = new_short_code
            db.commit()
            return JSONResponse(
                url_record.to_dict(),
                status_code=status.HTTP_202_ACCEPTED)
        except IntegrityError:
            db.rollback()
            return RedirectResponse(
                url=app.url_path_for("home"),
                status_code=status.HTTP_226_IM_USED)
