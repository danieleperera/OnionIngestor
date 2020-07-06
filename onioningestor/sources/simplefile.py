#!/usr/bin/python3
# -*- coding: utf-8 -*-

__author__ = 'Andrey Glauzer'
__license__ = "MIT"
__version__ = "1.0.1"
__maintainer__ = "Andrey Glauzer"
__status__ = "Development"

import requests
from pathlib import Path

from onioningestor.sources import Source


class Plugin(Source):

    def __init__(self, logger, name, filename):
        self.logger = logger
        self.name = name
        self.filename = filename
        super().__init__(self)


    def run(self):
        filepath = Path(__file__).parents[2]/self.filename
        with open(filepath, 'r') as fp:
            lines = fp.read().splitlines()
        for onion in lines:
            yield self.onion(url=onion,source='simple-file',type='domain')

