"""
tests for models.short_url_model
"""

from models.short_url_model import ShortURLModel
"""
Creating an object and printing it calls repr, successful print will return None
"""


def test_model_repr():
    short_url_model = ShortURLModel(
        url='https://example.test.url',
        short_code='testshort')
    assert print(short_url_model) is None
