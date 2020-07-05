<p align="center">
  <img src="docs/img/logo.png">
</p>

<h1 align="center">OnionIngestor</h1>
<p align="center">
  <a href="https://python.org/">
    <img src="https://img.shields.io/pypi/pyversions/3.svg">
  </a>
    <a href="https://opensource.org">
    <img src="https://img.shields.io/badge/Open%20Source-%E2%9D%A4-brightgreen.svg">
  </a>
</p>

<p align="center">
  An extendable tool to Collect, Crawl and Monitor onion sites on tor network and index collected information on Elasticsearch
</p>

## Introduction

OnionIngestor is based on ThreatIngestor tool structure to enable modular and extendable access for Cyber Threat Intelligence teams so that they can monitor and collect information on hidden sites over tor network.

The project is at it's early stages of development.

## To-do-list

- [ ] Add multiprocessing to improve analyzing speed
- [ ] Add more sources like reddit, gmail, pastebin, twitter and other hidden sites
- [ ] Add more operators like checking changes of the screenshots for monitoring sites, adding yara rules to eliminate false positives
- [ ] Add more notifiers like slack, smpt, discord

## Basic Implementation Logic

The OnionIngestor runs and managers 3 important type of classes:
Sources - These will collect hidden sites from clear net sources like pastebin, twitter, gist and crawled links
Operators - These will process the onion link. For example get the html, take screenshots and run other scanners like [onionscan](https://github.com/s-rah/onionscan)
Notifiers - These will notify the user - daily with a report and if any new changes has occured to a monitoring hidden site

OnionIngestor is designed to run as a daemon where it collects hidden sites from enabled sources and pass it to the operators and
when finished sleep until user defined time and restart the process from the beginning.
<p align="center">
  <img src="docs/img/workflow.png">
</p>

## Installation

Install requirements
    pip install -r requirements.txt

After the tor client and the installed libraries use the `--help` command to get details of its use.

```
python3 -m onionscraper --help

OnionScraper

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

optional arguments:
  -h, --help            show this help message and exit
  -c CONFIGFILE, --config CONFIGFILE
                        Path to config file
  --log {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        Set the logging level, default is INFO

```

The yaml config file contains all the information for OnionIngestor to work

### Operator [Onionscan](https://github.com/s-rah/onionscan)
	onionscan --mode analysis -verbose -webport 8081

To run the webapp by onionscan

## Output

The output of the result is json, and in the same format it is sent to the chosen syslog.

```
show output here
```
## Authors

Daniele Perera

## Acknowledgments 

Special thanks to:
andreyglauzer
InQuest
s-rah

Their code was used to implement this project
Feel free to fork or open an issue to collaborate with the project.

## License
This project is licensed under the [MIT](https://choosealicense.com/licenses/mit/) License - see the LICENSE.md file for details.
