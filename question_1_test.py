"""
Tests for question_1.py
"""

import random
from models import ShortURLModel
from question_1 import Codec
from sqlalchemy.orm import Session, declarative_base
from sqlalchemy import create_engine, select
from typing import List


def get_test_urls() -> List[str]:
    with open('input_urls.txt', 'r') as file:
        return file.read().splitlines()


def create_sqlite_session() -> Session:
    db = create_engine('sqlite:///url_records.db', echo=False, future=True)
    Base = declarative_base()
    Base.metadata.create_all(db)
    return Session(db)


def test_load_database_encode_decode(session=None) -> None:
    """
    Create and load test database in sqlite, a local file called url_records.db
    test the functionality as data is loaded by assuring the decoded url is the 
    same as the input url.
    """
    # create test database
    session = create_sqlite_session()

    # load test database
    codec = Codec()
    urls = get_test_urls()

    for url in urls:
        encoded = codec.encode(url, session)
        assert isinstance(encoded, str)
        # test test database
        decoded = codec.decode(encoded, session)
        assert isinstance(decoded, str)
        assert url == decoded

    session.close()


def test_update_url(session=None) -> None:
    """
    Encoding urls that are known to be present should update the short code.
    """
    session = create_sqlite_session()
    urls = get_test_urls()
    index = range(0, len(urls))

    # select 333 random urls and test the update
    for _ in range(333):
        i = random.choice(index)

        a_url = session.execute(select(ShortURLModel).where(
            ShortURLModel.url == urls[i])).first()
        assert isinstance(a_url, ShortURLModel)

        assert isinstance(codec.encode(urls[i], session), str)

        b_url = session.execute(select(ShortURLModel).where(
            ShortURLModel.url == urls[i])).first()
        assert isinstance(b_url, ShortURLModel)

        assert a_url.short_code != b_url.short_code

    session.close()


def test_decode(session=None) -> None:
    session = create_sqlite_session()
    codec = Codec()
    urls = get_test_urls()
    index = range(0, len(urls))
    # select 333 random urls and test the update
    for _ in range(333):
        i = random.choice(index)

        a_url = session.execute(select(ShortURLModel).where(
            ShortURLModel.url == urls[i])).first()
        assert isinstance(a_url, ShortURLModel)

        assert codec.decode(a_url.short_code, session) == a_url.url

    session.close()

test_load_database_encode_decode()