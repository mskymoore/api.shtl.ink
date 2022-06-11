"""
models.py: models for url shortener
"""

from sqlalchemy import Column, String
from sqlalchemy_serializer import SerializerMixin
from .database import Base


class ShortURLModel(Base, SerializerMixin):
    """
    ShortURLModel: Schema for database table with three columns, id(the primary key),
        url(the original url), and short_code, the shortened code keying the url
        in the databse.
    """
    __tablename__ = 'short_code_to_url'
    # 2000 characters is defacto max url length
    url = Column(String(2000), unique=True)
    short_code = Column(String(2000), primary_key=True)

    def __repr__(self):
        return f"URL(url={self.url!r}, \
                 short_code={self.short_code!r})"
