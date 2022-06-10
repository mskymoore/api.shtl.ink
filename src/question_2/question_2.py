# python3
# -*- coding: utf-8 -*-
"""
Chose api.shrtco.de/v2 because it's very simple, easy to use, and does not require authentication.
"""
import requests


class Codec:
    """
    Codec: Shortens long urls and returns original urls, urls are stored in a database.
    Codec.encode() takes a url string requests a short url from the api and returns it as a string
    Codec.decode() takes a shortened url string queries api for code and returns original url or None
    """

    def __init__(self):
        self.API_ENDPOINT = 'https://api.shrtco.de/v2'

    def encode(self, url: str) -> str:

        if len(url) > 2000:
            raise Exception(
                "URL is too long, de facto max length is 2000 characters.")

        response = requests.post(
            bytes(f"{self.API_ENDPOINT}/shorten?url={url}", encoding='utf8'))

        if response.status_code == 201:
            return response.json()['result']['short_link']

        else:
            raise Exception(
                f"Request failed with status code: {response.status_code}\nreason: {response.reason}")

    def decode(self, short_url: str) -> str:
        short_code = short_url.rsplit('/', maxsplit=1)[1]
        response = requests.get(
            bytes(
                f"{self.API_ENDPOINT}/info?code={short_code}",
                encoding='utf8'))

        if response.status_code == 200:
            return response.json()['result']['url']

        else:
            return None
