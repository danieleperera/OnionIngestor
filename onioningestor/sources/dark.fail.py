#!/usr/bin/python3
# -*- coding: utf-8 -*-

__author__ = 'Apurv Singh Gautam'
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Apurv Singh Gautam"
__status__ = "Development"


import requests
from lxml import html

from onioningestor.sources import Source

class Plugin(Source):

    def __init__(self, logger, name, domain, **kwargs):
        self.logger = logger
        self.name = name
        self.domain = domain
        super().__init__(self)


    def run(self):
    	self.logger.info('Getting onions from dark.fail')
    	lines = []

    	page = requests.get(domain) # Getting dark.fail HTML page
		tree = html.fromstring(page.content)
		lines = tree.xpath('//div[@class="online"]//code/text()') # Getting online onion links
        
        
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