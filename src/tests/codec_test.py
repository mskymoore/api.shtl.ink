"""
Tests for question_1.py
"""

import random

from requests import session

from shtl_ink_api.models import ShortURLModel, Base
from shtl_ink_api.codec import Codec
from sqlalchemy.orm import Session
from sqlalchemy import select, create_engine
from typing import List
from pytest import fixture, raises

SQLALCHEMY_DATABASE_URL = "sqlite:///./datatest.db.sqlite"
# SQLALCHEMY_DATABASE_URL = "postgresql://user:password@postgresserver/db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

Base.metadata.create_all(bind=engine)


def test_get_test_urls() -> List[str]:
    """
    test that test data is accessible
    """
    with open('data/input_urls.txt', 'r') as file:
        return file.read().splitlines()


@fixture
def a_codec() -> Codec:
    """
    test fixture to supply codec object
    """
    codec = Codec()
    yield codec


@fixture
def sql_session() -> Session:
    """
    test fixture to supply sqlite session
    """
    with Session(engine) as session:
        yield session


def test_url_length(a_codec, sql_session) -> None:
    """
    test that a url over 2000 characters raises an exception
    """
    with raises(Exception):
        a_codec.encode(str(['c' for c in range(2001)]), sql_session)


def test_absent_short_code(a_codec, sql_session) -> None:
    """
    test that any short code with an empty database returns None
    """
    assert a_codec.decode("SOmeBogusDatahere", sql_session) is None


def test_load_database_encode_decode(a_codec, sql_session) -> None:
    """
    Create and load test database in sqlite, a local file called url_records.db
    test the functionality as data is loaded by assuring the decoded url is the
    same as the input url.
    """

    # load test database
    urls = test_get_test_urls()

    for url in urls:
        encoded = a_codec.encode(url, sql_session)
        assert isinstance(encoded, str)
        # test test database
        decoded = a_codec.decode(encoded, sql_session)
        assert isinstance(decoded, str)
        assert url == decoded


def test_update_url(sql_session, a_codec) -> None:
    """
    Encoding urls that are known to be present should update the short code.
    """
    urls = test_get_test_urls()
    index = range(0, len(urls))

    # select 333 random urls and test the update
    for _ in range(333):
        i = random.choice(index)

        a_url_short_code = sql_session.execute(select(ShortURLModel).where(
            ShortURLModel.url == urls[i])).scalars().first().short_code

        assert isinstance(a_codec.encode(urls[i]), str)

        b_url_short_code = sql_session.execute(select(ShortURLModel).where(
            ShortURLModel.url == urls[i])).scalars().first().short_code

        assert isinstance(b_url_short_code, str)

        assert a_url_short_code != b_url_short_code


def test_decode(sql_session, a_codec) -> None:
    """
    test that decoding an short code gives the correct url
    """
    urls = test_get_test_urls()
    index = range(0, len(urls))
    # select 333 random urls and test the decode
    for _ in range(333):
        i = random.choice(index)

        a_url = sql_session.execute(select(ShortURLModel).where(
            ShortURLModel.url == urls[i])).scalars().first()

        assert a_codec.decode(a_url.short_code) == a_url.url
