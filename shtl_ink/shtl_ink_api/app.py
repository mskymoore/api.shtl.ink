from urllib import response
from fastapi import FastAPI, Depends, Request, Form, status
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse, JSONResponse, Response
from supertokens_python.recipe.session.framework.fastapi import verify_session
from supertokens_python.recipe.session import SessionContainer
from supertokens_python.framework.fastapi import get_middleware
from supertokens_python import get_all_cors_headers

from sqlalchemy import select, delete
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from pydantic import BaseModel
from .models import ShortURLModel, Base
from .codec import Codec
from .database import engine
from .config import frontend_base_url

Base.metadata.create_all(bind=engine)
codec = Codec()
app = FastAPI()

app.add_middleware(get_middleware())

app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_base_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"] + get_all_cors_headers(),
)


class ModificiationRequest(BaseModel):
    short_code: str
    new_short_code: str


class CreateRequest(BaseModel):
    url: str


class CreateCustomRequest(BaseModel):
    short_code: str
    url: str


class UrlRequest(BaseModel):
    short_code: str


def get_db():
    db = Session(engine)
    try:
        yield db
    finally:
        db.close()


def get_user_id(session):
    if session is not None:
        return session.get_user_id()
    else:
        return "anonymous"


def json_response_not_found(short_code):
    return JSONResponse(
        {"message": f"{short_code} not found"},
        status_code=status.HTTP_404_NOT_FOUND)


def json_response_in_use(short_code):
    return JSONResponse(
        {"message": f"{short_code} already in use"},
        status_code=status.HTTP_409_CONFLICT)


def json_response_not_owned(short_code):
    return JSONResponse(
        {"message": f"{short_code} not owned by you"},
        status_code=status.HTTP_403_FORBIDDEN)


def json_response_created(url_record):
    return JSONResponse(
        url_record.to_dict(),
        status_code=status.HTTP_201_CREATED)


def json_response_already_reported(url_record):
    return JSONResponse(
        url_record.to_dict(),
        status_code=status.HTTP_208_ALREADY_REPORTED)


def json_response_deleted(short_code, url):
    return JSONResponse(
        {"message": f"deleted record {short_code} -> {url}"},
        status_code=status.HTTP_200_OK)


def json_response_record(url_record):
    return JSONResponse(
        url_record.to_dict(),
        status_code=status.HTTP_200_OK)


def json_response_missing(something):
    return JSONResponse({"message": f"you must supply {something}"},
                        status_code=status.HTTP_406_NOT_ACCEPTABLE)


def json_response_failure():
    return JSONResponse(
        {"message": "something went wrong..."},
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
# all reserved endings that have no form data need to be before
# short code redirect reciever


@app.get("/")
async def root(request: Request):
    return RedirectResponse(
        url=frontend_base_url,
        status_code=status.HTTP_308_PERMANENT_REDIRECT)


@app.get("/all_short_codes")
async def get_all_records(
        db: Session = Depends(get_db),
        session: SessionContainer = Depends(verify_session(session_required=False))):

    user_id = get_user_id(session)
    url_records = db.execute(select(ShortURLModel).where(
        ShortURLModel.owner_id == user_id)).scalars().all()
    url_records = [url_record.to_dict() for url_record in url_records]
    return JSONResponse(url_records)


@app.get("/{short_code}")
async def go_to_url(
        short_code: str,
        db: Session = Depends(get_db)):

    url_record = db.get(ShortURLModel, (short_code))

    if url_record is None:
        return json_response_not_found(short_code)

    else:
        return RedirectResponse(
            url=url_record.url, status_code=status.HTTP_307_TEMPORARY_REDIRECT)

# all endpoints with form data


@app.post("/create_short_code")
async def create_short_code(
        create_request: CreateRequest,
        db: Session = Depends(get_db),
        session: SessionContainer = Depends(verify_session(session_required=False))):

    user_id = get_user_id(session)

    if create_request.url == '':
        return json_response_missing("a url")

    url_record = db.execute(
        select(ShortURLModel).where(
            ShortURLModel.url == create_request.url,
            ShortURLModel.owner_id == user_id)).scalars().first()

    if url_record is None:
        short_code = codec.encode(create_request.url, user_id, db)

    else:
        return json_response_already_reported(url_record)

    if isinstance(short_code, str):
        url_record = db.get(ShortURLModel, (short_code))
        return json_response_created(url_record)

    else:
        return json_response_failure()


@app.post("/create_custom_short_code")
async def create_custom_short_code(
        create_custom_request: CreateCustomRequest,
        db: Session = Depends(get_db),
        session: SessionContainer = Depends(verify_session(session_required=False))):

    user_id = get_user_id(session)

    if create_custom_request.short_code == '' or create_custom_request.url == '':
        return json_response_missing("a url and short code")

    url_record = db.get(ShortURLModel, (create_custom_request.short_code))

    if url_record is not None and url_record.url == create_custom_request.url and url_record.owner_id == user_id:
        return json_response_already_reported(url_record)

    if url_record is not None:
        return json_response_in_use(url_record.short_code)

    try:
        url_record = ShortURLModel(
            owner_id=user_id,
            url=create_custom_request.url,
            short_code=create_custom_request.short_code)
        db.add(url_record)
        db.commit()
        return json_response_created(url_record)

    except IntegrityError:
        db.rollback()
        return json_response_in_use(create_custom_request.short_code)


@app.post("/short_code")
async def Get_short_code_url(
        url_request: UrlRequest,
        db: Session = Depends(get_db)):

    if url_request.short_code == '':
        return json_response_missing("a short code")

    url_record = db.get(ShortURLModel, (url_request.short_code))

    if url_record is None:
        return json_response_not_found(url_request.short_code)

    else:
        return json_response_record(url_record)


@app.get("/short_code/{short_code}")
async def get_short_code_url(
        short_code: str,
        db: Session = Depends(get_db)):
    url_record = db.get(ShortURLModel, (short_code))

    if url_record is None:
        return json_response_not_found(short_code)

    else:
        return json_response_record(url_record)


@app.delete("/delete_short_code")
async def Delete_url_short_code(
        url_request: UrlRequest,
        db: Session = Depends(get_db),
        session: SessionContainer = Depends(verify_session(session_required=False))):

    user_id = get_user_id(session)

    if url_request.short_code == '':
        return json_response_missing("a short code")

    url_record = db.get(ShortURLModel, (url_request.short_code))

    if url_record is None:
        return json_response_not_found(url_request.short_code)

    if url_record.owner_id != user_id:
        return json_response_not_owned(url_record.short_code)

    try:
        url = url_record.url
        db.delete(url_record)
        db.commit()
        return json_response_deleted(url_request.short_code, url)

    except Exception as e:
        db.rollback()
        return json_response_failure()


@app.delete("/delete_short_code/{short_code}")
async def delete_url_short_code(
        short_code: str,
        db: Session = Depends(get_db),
        session: SessionContainer = Depends(verify_session(session_required=False))):

    user_id = get_user_id(session)

    url_record = db.get(ShortURLModel, (short_code))

    if url_record is None:
        return json_response_not_found(short_code)

    if url_record.owner_id != user_id:
        return json_response_not_owned(url_record.short_code)

    try:
        url = url_record.url
        db.delete(url_record)
        db.commit()
        return json_response_deleted(short_code, url)

    except Exception as e:
        db.rollback()
        print
        return json_response_failure()


@app.post("/modify_short_code")
async def modify_url_short_code(
        mod_request: ModificiationRequest,
        db: Session = Depends(get_db),
        session: SessionContainer = Depends(verify_session(session_required=False))):

    user_id = get_user_id(session)

    if mod_request.short_code == '' or mod_request.new_short_code == '':
        return json_response_missing("a short code and a new short code")

    url_record = db.get(ShortURLModel, (mod_request.short_code))
    conflict_url_record = db.get(ShortURLModel, (mod_request.new_short_code))

    if url_record is None:
        return json_response_not_found(mod_request.short_code)

    if url_record.owner_id != user_id:
        return json_response_not_owned(url_record.short_code)

    if conflict_url_record is not None:
        return json_response_in_use(mod_request.new_short_code)

    try:
        url_record.short_code = mod_request.new_short_code
        db.commit()
        return JSONResponse(
            url_record.to_dict(),
            status_code=status.HTTP_202_ACCEPTED)

    except IntegrityError:
        db.rollback()
        return json_response_in_use(mod_request.new_short_code)
