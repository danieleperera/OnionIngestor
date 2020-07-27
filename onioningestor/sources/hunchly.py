#!/usr/bin/python3
# -*- coding: utf-8 -*-

__author__ = 'Apurv Singh Gautam'
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Apurv Singh Gautam"
__status__ = "Development"

import xlrd
from pathlib import Path
from subprocess import call

from onioningestor.sources import Source


class Plugin(Source):

    def __init__(self, logger, name, domain, **kwargs):
        self.logger = logger
        self.name = name
        self.domain = domain
        super().__init__(self)


    def run(self):
    	self.logger.info('Getting onions from Hunchly')
    	lines = []
    	''' 
    	Hunchly Dropbox Link
    	https://www.dropbox.com/sh/wdleu9o7jj1kk7v/AADq2sapbxm7rVtoLOnFJ7HHa/HiddenServices.xlsx
    	'''
        call(['wget', self.domain]) # Downloading Hunchly spreadsheet file
        tmp_filename = 'HiddenServices.xlsx' # File name of Hunchly spreadsheet
        tmp_filepath = Path(__file__).parents[0]/tmp_filename # File path of the Hunchly spreadsheet
        workbook = xlrd.open_workbook(tmp_filepath) # Opening the Excel workbook
        worksheet = workbook.sheet_by_name('Up') # Selecting 'Up' domains sheet
        
        for row_idx in range(1, worksheet.nrows): # Iterate through rows
			lines.append(worksheet.cell(row_idx, 1).value) # Getting onion links
        
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

        call(['rm', tmp_filepath]) # Deleting the temp Hunchly file