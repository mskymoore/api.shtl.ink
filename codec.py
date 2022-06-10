# python3
# -*- coding: utf-8 -*-

import pytest
import random
from sqlalchemy import Column, String, create_engine, delete
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, declarative_base


# create database
db = create_engine('sqlite:///url_records.db', echo=False, future=True)
Base = declarative_base()


class ShortURLModel(Base):
    """
    ShortURLModel: Schema for database table with three columns, id(the primary key),
        long_url(the original url), and short_url(the shortened url)
    """
    __tablename__ = 'short_urls'
    # 2000 characters is defacto max url length
    long_url = Column(String(2000), unique=True)
    short_url = Column(String(2000), primary_key=True)

    def __repr__(self):
        return f"URL(id={self.id!r}, url={self.long_url!r}, \
                 short_url={self.short_url!r})"


Base.metadata.create_all(db)


def db_session(function):
    """
    @db_session: Decorator which uses a context manager to supply the decorated function
        with a sqlalchemy.orm.Session object
    get_session() Inner function of db_session decorator, checks kwargs for a Session and 
        supplies it to the passed function object with a context manager if it's absent
    """
    def get_session(*args, **kwargs):

        if 'session' in kwargs and isinstance(kwargs['session'], Session):
            short_url = function(*args, **kwargs)

        else:
            with Session(db) as session:
                short_url = function(session=session, *args, **kwargs)
                session.commit()
        return short_url
    return get_session


class Codec:
    """
    Codec: Shortens long urls and returns original urls, urls are stored in a database.
    Codec.primary_key_encode() takes a primary_key, a sqlalchemy.orm.Session object, and
        an optional multiplier returns a unique short code
    Codec.encode() takes a url string and a sqlalchemy.orm.Session object, overwrites or adds
        the record and returns the short code
    Codec.decode() takes a shortened url string and a sqlalchemy.orm.Session object, queries
        database for shortened url, returns original url or None
    """

    def __init__(self):
        # number of available urls in this config is 13,841,287,201
        # no vowels, no visually ambiguous characters
        self.alphabet = '23456789bcdfghjkmnpqrstvwxyzBCDFGHJKLMNPQRSTVWXYZ'
        self.base = len(self.alphabet) - 1
        # short code is 6 characters
        self.shift_range = range(2, 8)
        self.shift_bits = 12

    def url_encode(self, long_url: str, session: Session, multiplier=333) -> str:
        shift_bits = self.shift_bits
        short_url = ''
        seed = random.randint(1000, 13841287201)
        new_key = seed * multiplier

        for _ in self.shift_range:
            short_url += self.alphabet[(new_key >> shift_bits) & self.base]
            shift_bits -= 2

        try:
            session.add(ShortURLModel(long_url=long_url, short_url=short_url))
            session.commit()
            return short_url

        # short_url collision
        except IntegrityError as e:
            session.rollback()
            session.execute(delete(ShortURLModel).where(ShortURLModel.long_url == long_url))
            short_url = self.url_encode(long_url, session,
                                            multiplier=multiplier +
                                            random.choice(self.shift_range))
            return short_url
            # although this should work, it doesn't with sqllite
            # must delete and re-add instead, otherwise eventually a wrong url
            # is returned on decode
            # try:
            #     session.execute(update(ShortURLModel).where(
            #         ShortURLModel.long_url == long_url).values(short_url=short_url))
            #     session.commit()
            #     return short_url

            # except IntegrityError as e:
            #     session.rollback()
            #     short_url = self.url_encode(long_url, session,
            #                                 multiplier=multiplier +
            #                                 random.choice(self.shift_range))
            #     return short_url

    @db_session
    def encode(self, long_url: str, session=None) -> str:

        if len(long_url) > 2000:
            raise Exception("URL is too long, max length is 2000 characters.")

        return self.url_encode(long_url, session)

    @db_session
    def decode(self, short_url: str, session=None) -> str:
        url_record = session.get(ShortURLModel, (short_url))

        if url_record is not None:
            return url_record.long_url
        else:
            return None



if __name__ == "__main__":

    codec = Codec()

    with open("input_urls.txt", "r") as file:
        urls = file.read().splitlines()

    for i, url in enumerate(urls, 1):

        if i == 3000:
            break
        url = url.strip()
        encoded = codec.encode(url)
        decoded = codec.decode(encoded)

        if decoded != url:
            raise Exception("Returned the wrong url.")
        print(
            f"----------\nlong_url:  {url}\nshort_url: {encoded}\ndecoded:   {decoded}")
    # print(codec.decode("99"))
