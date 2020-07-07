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
import time
from bs4 import BeautifulSoup


class TORCH:
    def __init__(self,
                 port_proxy=None,
                 type_proxy=None,
                 server_proxy=None,
                 terms=None,
                 timeout=None):
        self.desktop_agents = [
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:60.0) Gecko/20100101 Firefox/60.0'
        ]
        self.url = 'http://xmh57jrzrnw6insl.onion'
        self.logger = logging.getLogger('Class:TORCH')
        self.session = requests.session()
        self.terms = terms
        self.timeout = timeout
        self.proxies = {
            "http": f"{type_proxy}://{server_proxy}:{port_proxy}",
        }
        # Seleciona um agent aleatório de acordo com a lista.

    @property
    def random_headers(self):
        return {
            'User-Agent': choice(self.desktop_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
        }

    @property
    def start(self):
        self.headers = self.random_headers
        self.logger.info(f'Conectando em {self.url}')

        urls = []
        self.logger.info('Gerando URLS')
        for term in self.terms:
            urls.append(
                f"{self.url}/4a1f6b371c/search.cgi?cmd=Search!&fmt=url&form=extended&GroupBySite=no&m=all&ps=50&q={term}&sp=1&sy=1&type=&ul=&wf=2221&wm=wrd")
            cont = 0
            while cont <= 9:
                cont += 1
                urls.append(
                    f"{self.url}/4a1f6b371c/search.cgi?cmd=Search!&fmt=url&form=extended&GroupBySite=no&m=all&np={cont}&ps=50&q={term}&sp=1&sy=1&type=&ul=&wf=2221&wm=wrd")
        onionurls = []
        for url in urls:
            self.logger.debug(f'Conectando em {url}')
            try:
                request = self.session.get(
                    url, proxies=self.proxies, timeout=self.timeout)

                if request.status_code == 200:
                    soup = BeautifulSoup(request.content, features="lxml")
                    for findurl in soup.find_all('dt'):
                        onionurls.append(findurl.find('a')['href'].replace('\xad', '')
                                                .replace('\n', '')
                                                .replace("http://", '')
                                                .replace("https://", '')
                                                .replace(r'\s', '')
                                                .replace('\t', ''))
            except(requests.exceptions.ConnectionError,
                   requests.exceptions.ChunkedEncodingError,
                   requests.exceptions.ReadTimeout,
                   requests.exceptions.InvalidURL) as e:
                self.logger.error(
                    f'Não consegui conectar na url, porque ocorreu um erro.\n{e}')
                pass
        return onionurls

if __name__ == '__main__':
    app = Reddit()
    app.start
