# python3
# -*- coding: utf-8 -*-

import random


class Codec:
    
    def __init__(self):
        self.url_dict = {}
        self.string_length = 6
        self.letters = ('abcdefghijklmnopqrstuvwxyzABCDEF'
                        'GHIJKLMNOPQRSTUVWXYZ0123456789')


    def generate_short_url(self):
        short_url = ''
        for i in range(self.string_length):
            short_url += random.choice(self.letters)
        
        while short_url not in self.url_dict:
            short_url = self.generate_short_url()

        return short_url


    def encode(self, long_url: str) -> str:
        short_url = generate_short_url()

        if long_url not in self.url_dict.keys():
            self.url_dict[short_url] = long_url
        else:
            self.url_dict = {k: v for k, v in self.url_dict.items() if v == long_url}
            self.url_dict[short_url] = long_url

        return short_url


    def decode(self, short_url: str) -> str:
        return self.url_dict[short_url]
