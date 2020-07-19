#!/usr/bin/python3
# -*- coding: utf-8 -*-

__author__ = 'Daniele Perera'
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Daniele Perera"
__status__ = "Development"

import os
import requests
from pathlib import Path

from onioningestor.sources import Source


class Plugin(Source):

    def __init__(self, logger, name, filename, **kwargs):
        self.logger = logger
        self.name = name
        self.filename = filename
        super().__init__(self)


    def run(self):
        items = []
        filepath = Path(__file__).parents[2]/self.filename
        with open(filepath, 'r') as fp:
            lines = fp.read().splitlines()
        for onion in lines:
            self.onionQueue.put(
                    (
                        2,
                        self.onion(
                            url=onion,
                            source=self.name,
                            type='domain',
                            status='offline',
                            monitor=False,
                            denylist=False)
                        )
                    )

