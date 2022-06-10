from question_1 import Codec
from sqlalchemy.orm import Session, declarative_base
from sqlalchemy import create_engine


def load(urls):
    # create test database
    db = create_engine('sqlite:///url_records.db', echo=False, future=True)
    Base = declarative_base()
    Base.metadata.create_all(db)

    # load test database
    codec = Codec()
    with Session(db) as session:
        for url in urls:
            url = url.strip()
            codec.encode(url, session)


if __name__ == "__main__":
    with open("input_urls.txt", "r") as file:
        urls = file.read().splitlines()
    load(urls)
