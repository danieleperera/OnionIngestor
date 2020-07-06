#!/usr/bin/python3
# -*- coding: utf-8 -*-

__author__ = 'Andrey Glauzer'
__license__ = "MIT"
__version__ = "1.0.1"
__maintainer__ = "Andrey Glauzer"
__status__ = "Development"

import requests
import json
import re
import logging
import re
import urllib.parse
from random import choice
from bs4 import BeautifulSoup


class Reddit:
    def __init__(self):
        self.session = requests.session()

        self.source = 'Reddit'

        self.url = 'https://api.pushshift.io/reddit/search/comment/?subreddit=onions&limit=1000000'
        self.desktop_agents = [
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:60.0) Gecko/20100101 Firefox/60.0']

    @property
    def random_headers(self):
        return {
            'User-Agent': choice(self.desktop_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
        }

    @property
    def start(self):
        self.reddit_json()

    def reddit_json(self):
        print('Getting Reddit API information')
        onionurl = []
        try:
            request = self.session.get(self.url,  headers=self.random_headers)

            loaded_json = json.loads(request.content)

            print(
                'Filtering the URLs that have the word .onion in the text')
            for data in loaded_json['data']:
                reddit_url = 'https://www.reddit.com{}'.format(
                    data['permalink'])
                try:
                    request = self.session.get(
                        reddit_url,  headers=self.random_headers)
                    soup = BeautifulSoup(request.content, features="lxml")

                    for raw in soup.findAll('a', {'rel': 'nofollow'}):
                        if 'https://' in raw['href']:
                            raw_text = self.raw(url=raw['href'])
                            if raw_text is not None:
                                print(
                                    'Applying REGEX. Wait...')
                                regex = re.compile(
                                    "[A-Za-z0-9]{0,12}\.?[A-Za-z0-9]{12,50}\.onion")

                                for lines in raw_text.split('\n'):
                                    rurls = lines \
                                        .replace('\xad', '') \
                                        .replace('\n', '') \
                                        .replace("http://", '') \
                                        .replace("https://", '') \
                                        .replace(r'\s', '') \
                                        .replace('\t', '')

                                    xurl = regex.match(rurls)
                                    if xurl is not None:
                                        onionurl.append(xurl.group())

                except(requests.exceptions.ConnectionError,
                       requests.exceptions.ChunkedEncodingError,
                       requests.exceptions.ReadTimeout,
                       requests.exceptions.InvalidURL) as e:
                    print(
                        'Não consegui conectar na url, porque ocorreu um erro.\n{e}'.format(e=e))

        except(requests.exceptions.ConnectionError,
               requests.exceptions.ChunkedEncodingError,
               requests.exceptions.ReadTimeout,
               requests.exceptions.InvalidURL) as e:
            print(
                'Não consegui conectar na url, porque ocorreu um erro.\n{e}'.format(e=e))

        return onionurl

    def raw(self, url):
        try:
            if url is not None:
                request = self.session.get(url, headers=self.random_headers)
                print(
                    'Connecting in {url} - {status}'.format(url=url, status=request.status_code))

                if request.status_code == 200:

                    soup = BeautifulSoup(request.content, features="lxml")
                    for s in soup(['script', 'style']):
                        s.decompose()

                    return ' '.join(soup.stripped_strings)

        except (requests.exceptions.ConnectionError,
                requests.exceptions.ChunkedEncodingError,
                requests.exceptions.ReadTimeout,
                requests.exceptions.TooManyRedirects) as e:
            pass

if __name__ == '__main__':
    app = Reddit()
    app.start
