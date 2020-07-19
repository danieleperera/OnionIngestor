"""OnionScraper

A Python3 application for indexing and scraping hidden services ElasticSearch

Installation:
   This application assumes you have python3 and pip3 installed.

   pip3 install -r requirements.txt


This software is provided subject to the MIT license stated below.
--------------------------------------------------
        MIT License

        Permission is hereby granted, free of charge, to any person obtaining a copy
        of this software and associated documentation files (the "Software"), to deal
        in the Software without restriction, including without limitation the rights
        to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
        copies of the Software, and to permit persons to whom the Software is
        furnished to do so, subject to the following conditions:

        The above copyright notice and this permission notice shall be included in all
        copies or substantial portions of the Software.

        THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
        IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
        FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
        AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
        LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
        OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
        SOFTWARE.
--------------------------------------------------
"""
import argparse

from onioningestor import Ingestor


# Load arguments from user
parser = argparse.ArgumentParser(
        prog='onioningestor',
        description=__doc__,formatter_class=argparse.RawDescriptionHelpFormatter)
parser.add_argument('-c', '--config',dest="configFile", required = True, help='Path to config file')
parser.add_argument("--log", dest="logLevel",default='INFO', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], help="Set the logging level, default is INFO")

args = parser.parse_args()
app = Ingestor(args)

app.run()
