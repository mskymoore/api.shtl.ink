from question_1 import Codec
from sqlalchemy.orm import Session, declarative_base
from sqlalchemy import create_engine
from time import time


# create database
db = create_engine('sqlite:///url_records.db', echo=False, future=True)
Base = declarative_base()
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


def test(urls):
    codec = Codec()
    num_urls = len(urls)
    t1 = time()
    with Session(db) as session:
        for url in urls:
            url = url.strip()

            encoded = codec.encode(url, session)
            decoded = codec.decode(encoded, session)

            if decoded != url:
                raise Exception("Returned the wrong url.")
            # print(
            #     f"----------\nlong_url:  {url}\nshort_url: " +
            #     f"{encoded}\ndecoded:   {decoded}")
    t2 = time()
    execution_time = t2 - t1
    print(
        f"Processed in {num_urls} urls in {(execution_time):.3f}s" +
        f"\n{num_urls/execution_time:.1f} urls per second")


if __name__ == "__main__":
    with open("input_urls.txt", "r") as file:
        urls = file.read().splitlines()
    test(urls)
