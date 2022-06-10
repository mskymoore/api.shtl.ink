"""
Tests for question_2.question_2
"""

import random
from time import sleep
from question_2.question_2 import Codec
from typing import List
from pytest import fixture, raises


@fixture
def a_codec() -> Codec:
    """
    test fixture to provide access to the codec object
    """
    codec = Codec()
    yield codec


def test_get_test_urls() -> List[str]:
    """
    test that the test input data is readable
    """
    with open('data/input_urls.txt', 'r') as file:
        return file.read().splitlines()


def test_absent_short_code(a_codec) -> None:
    """
    test that any bogus short code returns None
    """
    assert a_codec.decode("nota/SOmeBogusDatahere") is None


def test_url_length(a_codec) -> None:
    """
    test that a url with more than 2000 characters raises an exception
    """
    with raises(Exception):
        a_codec.encode(str(['c' for c in range(2001)]))


def test_encode_failure(a_codec) -> None:
    """
    test that trying to encode a string that isn't a url raises an exception
    """
    with raises(Exception):
        a_codec.encode("NotAurl")


def test_encode_decode() -> None:
    """
    test that the short code of an encoded url is decoded to the original url
    """
    codec = Codec()
    urls = test_get_test_urls()
    index = range(0, len(urls))
    # select 333 random urls and test the decode

    for _ in range(10):
        i = random.choice(index)
        a_url_short_code = codec.encode(urls[i])

        assert isinstance(a_url_short_code, str)

        # sleep(1)
        a_url = codec.decode(a_url_short_code)

        assert isinstance(a_url, str)

        # api service strips # and & endings
        assert a_url == urls[i].split(
            '#', maxsplit=1)[0].split(
            '&', maxsplit=1)[0]
