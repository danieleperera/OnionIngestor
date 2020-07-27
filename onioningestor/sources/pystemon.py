#!/usr/bin/python3
# -*- coding: utf-8 -*-

__author__ = 'Apurv Singh Gautam'
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Apurv Singh Gautam"
__status__ = "Development"


import os
from pathlib import Path
from subprocess import call

from onioningestor.sources import Source


class Plugin(Source):

    def __init__(self, logger, dirname, **kwargs):
        self.logger = logger
        self.dirname = dirname
        super().__init__(self)


    def run(self):
    	self.logger.info('Getting onions from Pystemon')
        dirpath = Path(__file__).parents[1]/self.dirname # Directory path of Pystemon alerts
        for subdir, dirs, files in os.walk(dirpath) # Getting the files from pystemon alerts directory
            for filename in files: 
                name = subdir.split('/')[5] # Paste Source Name
                filepath = subdir + os.sep + filename 

                with open(filepath, 'r') as f:
                    lines = f.readlines()

                for onion in lines:
                    self.onionQueue.put(
                        (
                            2,
                            self.onion(
                                url=onion,
                                source=name,
                                type='domain',
                                status='offline',
                                monitor=False,
                                denylist=False)
                            )
                        )
                call(['rm', filepath]) # Deleting the temp alert paste file