from urllib import response
from fastapi import FastAPI, Depends, Request, Form, status

from starlette.responses import RedirectResponse, JSONResponse, Response

from sqlalchemy import select, delete
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from .models import ShortURLModel, Base
from .codec import Codec
from .database import engine

Base.metadata.create_all(bind=engine)
codec = Codec()
app = FastAPI()


def get_db():
    db = Session(engine)
    try:
        yield db
    finally:
        db.close()


def json_response_not_found(short_code):
    return JSONResponse(
        {"message": f"{short_code} not found"},
        status_code=status.HTTP_404_NOT_FOUND)


def json_response_in_use(short_code):
    return JSONResponse(
        {"message": f"{short_code} already in use"},
        status_code=status.HTTP_409_CONFLICT)


def json_response_created(url_record):
    return JSONResponse(
        url_record.to_dict(),
        status_code=status.HTTP_201_CREATED)


@app.get("/")
def root(request: Request, db: Session = Depends(get_db)):
    coded_urls = db.execute(select(ShortURLModel)).scalars().all()
    return Response()


@app.get("/{short_code}")
def go_to_url(
        request: Request,
        short_code: str,
        db: Session = Depends(get_db)):

    url_record = db.get(ShortURLModel, (short_code))

    if url_record is None:
        return json_response_not_found(short_code)

    else:
        return RedirectResponse(
            url=url_record.url, status_code=status.HTTP_307_TEMPORARY_REDIRECT)


@app.post("/create")
def create_url_short_code(
        request: Request,
        url: str = Form(...),
        db: Session = Depends(get_db)):

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
        return json_response_created(url_record)

    else:
        return JSONResponse(
            {"message": "something went wrong..."},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@app.post("/create_custom")
def create_custom_url_short_code(
        request: Request,
        url: str = Form(...),
        short_code: str = Form(...),
        db: Session = Depends(get_db)):

    try:
        url_record = ShortURLModel(url=url, short_code=short_code)
        db.add(url_record)
        db.commit()
        return json_response_created(url_record)

    except IntegrityError:
        db.rollback()
        return json_response_in_use(short_code)


@app.get("/get/{short_code}")
def get_short_code_url(
        request: Request,
        short_code: str,
        db: Session = Depends(get_db)):

    url_record = db.get(ShortURLModel, (short_code))

    if url_record is None:
        return json_response_not_found(short_code)

    else:
        return JSONResponse(
            url_record.to_dict(),
            status_code=status.HTTP_200_OK)


@app.get("/delete/{short_code}")
def delete_url_short_code(
        request: Request,
        short_code: str,
        db: Session = Depends(get_db)):

    url_record = db.get(ShortURLModel, (short_code))

    if url_record is None:
        return json_response_not_found(short_code)
    try:
        url = url_record.url
        db.delete(url_record)
        db.commit()
        return JSONResponse(
            {"message": f"deleted record {short_code} -> {url}"},
            status_code=status.HTTP_200_OK)

    except Exception as e:
        db.rollback()
        print
        return RedirectResponse(
            url=app.url_path_for("root"),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@app.post("/modify/{short_code}")
def modify_url_short_code(
        request: Request,
        short_code: str,
        new_short_code: str = Form(...),
        db: Session = Depends(get_db)):

    url_record = db.get(ShortURLModel, (short_code))
    conflict_url_record = db.get(ShortURLModel, (new_short_code))

    if url_record is None:
        return json_response_not_found(short_code)

    if conflict_url_record is not None:
        return json_response_in_use(new_short_code)

    try:
        url_record.short_code = new_short_code
        db.commit()
        return JSONResponse(
            url_record.to_dict(),
            status_code=status.HTTP_202_ACCEPTED)

    except IntegrityError:
        db.rollback()
        return json_response_in_use(new_short_code)
