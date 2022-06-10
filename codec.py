# python3
# -*- coding: utf-8 -*-

import pytest
import random
from sqlalchemy import Column, Integer, String, create_engine, delete
from sqlalchemy.orm import Session, declarative_base


# create database
db = create_engine('sqlite:///url_records.db', echo=False, future=True)
Base = declarative_base()


class URLTable(Base):
    """
    URLTable: Schema for database table with three columns, id(the primary key),
        long_url(the original url), and short_url(the shortened url)
    """
    __tablename__ = 'short_urls'
    id = Column(Integer, primary_key=True)
    # 2000 characters is defacto max url length
    long_url = Column(String(2000))
    short_url = Column(String(2000))

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
        # no vowels, no visually ambiguous characters
        self.alphabet = '23456789bcdfghjkmnpqrstvwxyzBCDFGHJKLMNPQRSTVWXYZ'
        self.base = len(self.alphabet) - 1
        # short code is 6 characters
        self.shift_range = range(2, 8)
        self.shift_bits = 12

    def primary_key_encode(self, primary_key: int, session: Session, multiplier=333) -> str:
        shift_bits = self.shift_bits
        short_url = ''
        new_key = primary_key * multiplier

        for _ in self.shift_range:
            short_url += self.alphabet[(new_key >> shift_bits) & self.base]
            shift_bits -= 2

        url_records = session.query(URLTable)\
            .filter(URLTable.short_url == short_url).all()

        if len(url_records) != 0:
            # collision
            short_url = self.primary_key_encode(primary_key, session,
                                                multiplier=multiplier +
                                                random.choice(self.shift_range))
        return short_url

    @db_session
    def encode(self, long_url: str, session=None) -> str:
        
        if len(long_url) > 2000:
            raise Exception("URL is too long, max length is 2000 characters.")

        # check for url in db
        url_record = session.query(URLTable)\
            .filter(URLTable.long_url == long_url).first()

        # add if not present
        if url_record is None:
            session.add(URLTable(long_url=long_url, short_url=""))
            url_record = session.query(URLTable)\
                .filter(URLTable.long_url == long_url).first()
            short_url = self.primary_key_encode(url_record.id, session)
            setattr(url_record, 'short_url', short_url)
            return short_url

        # overwrite if present
        else:
            session.execute(delete(URLTable)
                            .where(URLTable.id == url_record.id))
            short_url = self.encode(long_url, session=session)

        return short_url

    @db_session
    def decode(self, short_url: str, session=None) -> str:
        url_records = session.query(URLTable)\
            .filter(URLTable.short_url == short_url).all()

        num_records = len(url_records)
        if num_records > 1:
            raise Exception("More than one record returned.")
        elif num_records == 0:
            return None
        else:
            return url_records[0].long_url


if __name__ == "__main__":

    codec = Codec()

    with open("input_urls.txt", "r") as file:
        urls = file.read().splitlines()

    for i, url in enumerate(urls, 1):
        url = url.strip()
        encoded = codec.encode(url)
        decoded = codec.decode(encoded)
        if decoded != url:
            raise Exception("Returned the wrong url.")
        print(
            f"----------\nlong_url:  {url}\nshort_url: {encoded}\ndecoded:   {decoded}")
    # print(codec.decode("99"))
