"""
Tests for question_1.py
"""

import random
from models.ShortURLModel import ShortURLModel, Base
from question_1.question_1 import Codec, db
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List
from pytest import fixture


def test_get_test_urls() -> List[str]:
    with open('data/input_urls.txt', 'r') as file:
        return file.read().splitlines()


@fixture
def a_codec() -> Codec:
    codec = Codec()
    yield codec


@fixture
def sqlite_session() -> Session:
    with Session(db) as session:
        yield session


def test_load_database_encode_decode(a_codec) -> None:
    """
    Create and load test database in sqlite, a local file called url_records.db
    test the functionality as data is loaded by assuring the decoded url is the
    same as the input url.
    """

    # load test database
    urls = test_get_test_urls()

    for url in urls:
        encoded = a_codec.encode(url)
        assert isinstance(encoded, str)
        # test test database
        decoded = a_codec.decode(encoded)
        assert isinstance(decoded, str)
        assert url == decoded


def test_update_url(sqlite_session, a_codec) -> None:
    """
    Encoding urls that are known to be present should update the short code.
    """
    urls = test_get_test_urls()
    index = range(0, len(urls))

    # select 333 random urls and test the update
    for _ in range(333):
        i = random.choice(index)

        a_url_short_code = sqlite_session.execute(select(ShortURLModel).where(
            ShortURLModel.url == urls[i])).scalars().first().short_code

        assert isinstance(a_codec.encode(urls[i]), str)

        b_url_short_code = sqlite_session.execute(select(ShortURLModel).where(
            ShortURLModel.url == urls[i])).scalars().first().short_code

        assert a_url_short_code != b_url_short_code


def test_decode(sqlite_session, a_codec) -> None:
    urls = test_get_test_urls()
    index = range(0, len(urls))
    # select 333 random urls and test the decode
    for _ in range(333):
        i = random.choice(index)

        a_url = sqlite_session.execute(select(ShortURLModel).where(
            ShortURLModel.url == urls[i])).scalars().first()

        assert a_codec.decode(a_url.short_code) == a_url.url
