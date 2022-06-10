# python3
# -*- coding: utf-8 -*-

import random
from models import ShortURLModel
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

    def url_encode(self, long_url: str, session: Session, multiplier: int) -> str:
        shift_bits = self.shift_bits
        short_url = ''
        # The number of available urls in this config is 13,983,816 by nCk(nChoosek)
        # where n is the total number of characters available and k is the number
        # of characters in the short code.  Don't know if it's possible to have
        # a bijective algorithim with fixed output length.
        # TODO: research bijective algorithm with fixed output length

        seed = random.randint(3333, 13983816)
        key = seed * multiplier

        for _ in self.shifts:
            short_url += self.alphabet[(key >> shift_bits) & self.base]
            shift_bits -= 2

        try:
            session.add(ShortURLModel(long_url=long_url, short_url=short_url))
            session.commit()
            return short_url

        # collision
        except IntegrityError:
            session.rollback()
            session.execute(delete(ShortURLModel).where(
                ShortURLModel.long_url == long_url))
            short_url = self.url_encode(long_url, session,
                multiplier + random.choice(self.shifts))
            return short_url

    def encode(self, long_url: str, session: Session) -> str:

        if len(long_url) > 2000:
            raise Exception("URL is too long, max length is 2000 characters.")

        return self.url_encode(long_url, session, self.multiplier)

    def decode(self, short_url: str, session: Session) -> str:
        url_record = session.get(ShortURLModel, (short_url))

        if url_record is None:
            return None

        else:
            return url_record.long_url
