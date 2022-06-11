# python3
# -*- coding: utf-8 -*-

import random
from src.models.short_url_model import ShortURLModel, Base
from sqlalchemy import delete
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError


class Codec:
    """
    Codec: Shortens long urls and returns original urls, urls are stored in a database.
    Codec.url_encode() takes a long url, a sqlalchemy.orm.Session object, and
        a multiplier returns a unique short code
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
        self.shifts = range(2, 8)
        self.shift_bits = 12
        self.multiplier = 333

    def url_encode(
            self,
            url: str,
            multiplier: int,
            session: Session,
            first_short_code: str = '') -> str:
        shift_bits = self.shift_bits
        short_code = ''
        # The number of available urls in this config is 13,983,816 by nCk(nChoosek)
        # where n is the total number of characters available and k is the number
        # of characters in the short code.  Don't know if it's possible to have
        # a bijective algorithim with fixed output length.
        # TODO: research bijective algorithm with fixed output length

        seed = random.randint(3333, 13983816)
        key = seed * multiplier

        for _ in self.shifts:
            short_code += self.alphabet[(key >> shift_bits) & self.base]
            shift_bits -= 2

        if first_short_code == short_code:
            short_code = self.url_encode(
                url,
                multiplier +
                random.choice(
                    self.shifts),
                session, first_short_code=short_code)
            return short_code

        try:
            session.add(ShortURLModel(
                url=url, short_code=short_code))
            session.commit()
            return short_code

        # collision
        except IntegrityError:
            session.rollback()

            # collision on short_code
            if session.get(ShortURLModel, (short_code)) is None:
                short_code = self.url_encode(
                    url,
                    multiplier +
                    random.choice(
                        self.shifts),
                    session)
                return short_code

            # collision on url
            else:
                session.execute(delete(ShortURLModel).where(
                    ShortURLModel.url == url))
                short_code = self.url_encode(
                    url,
                    multiplier +
                    random.choice(
                        self.shifts),
                    session, first_short_code=short_code)
                return short_code

    def encode(self, url: str, session: Session) -> str:

        if len(url) > 2000:
            raise Exception(
                "URL is too long, de facto max length is 2000 characters.")

        return self.url_encode(url, self.multiplier, session)

    def decode(self, short_code: str, session: Session) -> str:
        url_record = session.get(ShortURLModel, (short_code))

        if url_record is None:
            return None

        else:
            return url_record.url
