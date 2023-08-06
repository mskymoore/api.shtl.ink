"""
models.py: models for url shortener
"""

from email.policy import default
from sqlalchemy import Column, String
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel

Base = declarative_base()

class ShortURLModel(Base, SerializerMixin):
    """
    ShortURLModel: Schema for database table with three columns, id(the primary key),
        url(the original url), and short_code, the shortened code keying the url
        in the databse.
    """

    __tablename__ = "short_code_to_url"
    # 2000 characters is defacto max url length
    owner_id = Column(String(2000), unique=False, default="anonymous")
    url = Column(String(2000), unique=False)
    short_code = Column(String(2000), primary_key=True)

    def __repr__(self):
        return f"URL(url={self.url!r}, \
                 short_code={self.short_code!r})"
    

class ModificiationRequest(BaseModel):
    short_code: str
    new_short_code: str


class CreateRequest(BaseModel):
    url: str


class CreateCustomRequest(BaseModel):
    short_code: str
    url: str


class UrlRequest(BaseModel):
    short_code: str
