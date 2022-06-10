"""models.py: models for url shortener"""

from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, String

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
