"""
Tests for question_2.py
"""

import random
from time import sleep
from question_2.question_2 import Codec
from typing import List


def test_get_test_urls() -> List[str]:
    with open('data/input_urls.txt', 'r') as file:
        return file.read().splitlines()


def test_encode_decode() -> None:
    codec = Codec()
    urls = test_get_test_urls()
    index = range(0, len(urls))
    # select 333 random urls and test the decode
    for _ in range(3):
        i = random.choice(index)

        a_url_short_code = codec.encode(urls[i])

        assert isinstance(a_url_short_code, str)

        sleep(0.5)
        a_url = codec.decode(a_url_short_code)

        assert isinstance(a_url, str)

        assert a_url == urls[i]


if __name__ == '__main__':
    test_encode_decode()