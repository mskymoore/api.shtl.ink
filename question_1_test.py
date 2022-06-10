"""
Tests for question_1.py
"""

import random

from models import ShortURLModel, Base
from question_1 import Codec
from sqlalchemy.orm import Session
from sqlalchemy.engine import Engine
from sqlalchemy import create_engine, select
from typing import List
from pytest import fixture
from pathlib import Path


def test_get_test_urls() -> List[str]:
    with open('input_urls.txt', 'r') as file:
        return file.read().splitlines()


@fixture
def sqlite_file() -> Engine:
    db_path = Path('url_records.db')
    db = create_engine(f"sqlite:///{db_path}", echo=False, future=True)
    Base.metadata.create_all(db)
    yield db


@fixture
def sqlite_session(sqlite_file) -> Session:
    with Session(sqlite_file) as session:
        yield session


def test_load_database_encode_decode(sqlite_session) -> None:
    """
    Create and load test database in sqlite, a local file called url_records.db
    test the functionality as data is loaded by assuring the decoded url is the 
    same as the input url.
    """

    # load test database
    codec = Codec()
    urls = test_get_test_urls()

    for url in urls:
        encoded = codec.encode(url, sqlite_session)
        assert isinstance(encoded, str)
        # test test database
        decoded = codec.decode(encoded, sqlite_session)
        assert isinstance(decoded, str)
        assert url == decoded


def test_update_url(sqlite_session) -> None:
    """
    Encoding urls that are known to be present should update the short code.
    """
    urls = test_get_test_urls()
    index = range(0, len(urls))
    codec = Codec()

    # select 333 random urls and test the update
    for _ in range(333):
        i = random.choice(index)

        a_url_short_code = sqlite_session.execute(select(ShortURLModel).where(
            ShortURLModel.url == urls[i])).scalars().first().short_code

        assert isinstance(codec.encode(urls[i], sqlite_session), str)

        b_url_short_code = sqlite_session.execute(select(ShortURLModel).where(
            ShortURLModel.url == urls[i])).scalars().first().short_code

        assert a_url_short_code != b_url_short_code


def test_decode(sqlite_session) -> None:
    codec = Codec()
    urls = test_get_test_urls()
    index = range(0, len(urls))
    # select 333 random urls and test the decode
    for _ in range(333):
        i = random.choice(index)

        a_url = sqlite_session.execute(select(ShortURLModel).where(
            ShortURLModel.url == urls[i])).scalars().first()

        assert codec.decode(a_url.short_code, sqlite_session) == a_url.url
