from fastapi import FastAPI, Depends, Request, status
from fastapi.middleware.cors import CORSMiddleware
from armasec import OpenidConfigLoader, TokenManager, TokenDecoder, TokenSecurity
from armasec.schemas.armasec_config import DomainConfig
from armasec.token_security import ManagerConfig
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
from .codec import Codec
from .database import engine
from .config import frontend_base_url, oidc_audience, oidc_issuer

log = getLogger(__name__)
log.info("Logger initialized, starting shtl_ink_api...")

Base.metadata.create_all(bind=engine)
codec = Codec()
app = FastAPI()

openid_config = OpenidConfigLoader(
    domain=oidc_issuer, use_https=True, debug_logger=log.debug
)

domain_config = DomainConfig(domain=oidc_issuer, audience=oidc_audience)

# decode_options_override = {"verify_exp": False}
# decode_options_override = {}

token_decoder = TokenDecoder(
    jwks=openid_config.jwks,
    debug_logger=log.debug,
    # decode_options_override=decode_options_override,
)

token_manager = TokenManager(
    openid_config=openid_config,
    token_decoder=token_decoder,
    audience=oidc_audience,
    debug_logger=log.debug,
)

token_manager_config = ManagerConfig(manager=token_manager, domain_config=domain_config)

armasec = TokenSecurity(
    domain_configs=[domain_config], debug_logger=log.debug  # , debug_exceptions=True
)
armasec.managers = [token_manager_config]

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


@app.get("/all_short_codes", dependencies=[Depends(armasec)])
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
@app.post("/create_short_code")
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
