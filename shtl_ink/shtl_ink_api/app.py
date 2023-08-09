from fastapi import FastAPI, Depends, Request, status
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse, JSONResponse
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from logging import getLogger

from .responses import json_response_already_reported, json_response_created
from .responses import json_response_failure, json_response_missing
from .responses import json_response_not_found, json_response_not_owned
from .responses import json_response_deleted, json_response_record
from .responses import json_response_in_use
from .models import ShortURLModel, ModificiationRequest, UrlRequest
from .models import CreateRequest, CreateCustomRequest, Base
from .models import AuthenticationRequest, AuthenticationRefreshRequest
from armasec import OpenidConfigLoader
from .keycloak_armasec import KeycloakArmasec
from .get_token import get_oidc_token, refresh_oidc_token
from .codec import Codec
from .database import engine
from .config import frontend_base_url, oidc_audience, oidc_issuer
from .config import client_id, client_secret

log = getLogger(__name__)
log.info("Logger initialized, starting shtl_ink_api...")

Base.metadata.create_all(bind=engine)
codec = Codec()
app = FastAPI()

armasec = KeycloakArmasec(domain=oidc_issuer, audience=oidc_audience)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_base_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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


# all reserved endings that have no form data need to be before
# short code redirect reciever
@app.get("/")
async def root(request: Request):
    return RedirectResponse(
        url=frontend_base_url, status_code=status.HTTP_308_PERMANENT_REDIRECT
    )


@app.get(
    "/all_short_codes", dependencies=[Depends(armasec.lockdown("get:all_short_codes"))]
)
async def get_all_records(db: Session = Depends(get_db)):
    user_id = "anonymous"
    url_records = (
        db.execute(select(ShortURLModel).where(ShortURLModel.owner_id == user_id))
        .scalars()
        .all()
    )
    url_records = [url_record.to_dict() for url_record in url_records]
    return JSONResponse(url_records)


@app.get("/{short_code}")
async def go_to_url(short_code: str, db: Session = Depends(get_db)):
    url_record = db.get(ShortURLModel, (short_code))

    if url_record is None:
        return json_response_not_found(short_code)

    else:
        return RedirectResponse(
            url=url_record.url, status_code=status.HTTP_307_TEMPORARY_REDIRECT
        )


# all endpoints with form data
@app.post("/auth")
async def auth(auth_request: AuthenticationRequest):
    access_token, refresh_token = get_oidc_token(
        auth_request.username,
        auth_request.password,
        oidc_issuer,
        client_id,
        client_secret,
    )
    if access_token is None:
        return json_response_failure()
    else:
        return JSONResponse(
            {"access_token": access_token, "refresh_token": refresh_token}
        )


@app.post("/auth/refresh")
async def auth_refresh(auth_refresh_request: AuthenticationRefreshRequest):
    access_token, refresh_token = refresh_oidc_token(
        oidc_issuer,
        client_id,
        client_secret,
        auth_refresh_request.refresh_token,
    )
    if access_token is None:
        return json_response_failure()
    else:
        return JSONResponse(
            {"access_token": access_token, "refresh_token": refresh_token}
        )


@app.post(
    "/create_short_code",
    dependencies=[Depends(armasec.lockdown("post:create_short_code"))],
)
async def create_short_code(
    create_request: CreateRequest,
    db: Session = Depends(get_db),
):
    user_id = "anonymous"

    if create_request.url == "":
        return json_response_missing("a url")

    url_record = (
        db.execute(
            select(ShortURLModel).where(
                ShortURLModel.url == create_request.url,
                ShortURLModel.owner_id == user_id,
            )
        )
        .scalars()
        .first()
    )

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
):
    user_id = "anonymous"

    if create_custom_request.short_code == "" or create_custom_request.url == "":
        return json_response_missing("a url and short code")

    url_record = db.get(ShortURLModel, (create_custom_request.short_code))

    if (
        url_record is not None
        and url_record.url == create_custom_request.url
        and url_record.owner_id == user_id
    ):
        return json_response_already_reported(url_record)

    if url_record is not None:
        return json_response_in_use(url_record.short_code)

    try:
        url_record = ShortURLModel(
            owner_id=user_id,
            url=create_custom_request.url,
            short_code=create_custom_request.short_code,
        )
        db.add(url_record)
        db.commit()
        return json_response_created(url_record)

    except IntegrityError as e:
        log.error(e)
        db.rollback()
        return json_response_in_use(create_custom_request.short_code)


@app.post("/short_code")
async def Get_short_code_url(url_request: UrlRequest, db: Session = Depends(get_db)):
    if url_request.short_code == "":
        return json_response_missing("a short code")

    url_record = db.get(ShortURLModel, (url_request.short_code))

    if url_record is None:
        return json_response_not_found(url_request.short_code)

    else:
        return json_response_record(url_record)


@app.get("/short_code/{short_code}")
async def get_short_code_url(short_code: str, db: Session = Depends(get_db)):
    url_record = db.get(ShortURLModel, (short_code))

    if url_record is None:
        return json_response_not_found(short_code)

    else:
        return json_response_record(url_record)


@app.delete("/delete_short_code")
async def Delete_url_short_code(
    url_request: UrlRequest,
    db: Session = Depends(get_db),
):
    user_id = "anonymous"

    if url_request.short_code == "":
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
        log.error(e)
        db.rollback()
        return json_response_failure()


@app.delete("/delete_short_code/{short_code}")
async def delete_url_short_code(
    short_code: str,
    db: Session = Depends(get_db),
):
    user_id = "anonymous"

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
        log.error(e)
        db.rollback()
        return json_response_failure()


@app.post("/modify_short_code")
async def modify_url_short_code(
    mod_request: ModificiationRequest,
    db: Session = Depends(get_db),
):
    user_id = "anonymous"

    if mod_request.short_code == "" or mod_request.new_short_code == "":
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
        return JSONResponse(url_record.to_dict(), status_code=status.HTTP_202_ACCEPTED)

    except IntegrityError as e:
        log.error(e)
        db.rollback()
        return json_response_in_use(mod_request.new_short_code)
