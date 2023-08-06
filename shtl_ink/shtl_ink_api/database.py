from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .config import db_host, db_name, db_user, db_pass


if db_host is not None:
    SQLALCHEMY_DATABASE_URL = f"postgresql://{db_user}:{db_pass}@{db_host}/{db_name}"
    connect_args = {}

else:
    SQLALCHEMY_DATABASE_URL = "sqlite:///sqlite.db"
    connect_args = {"check_same_thread": False}

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args=connect_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
