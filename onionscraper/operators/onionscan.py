import re
import os
import sys
import json
import time
import random
import traceback
import subprocess
from uuid import uuid4
from pathlib import Path
from datetime import datetime as dt
from json.decoder import JSONDecodeError
from concurrent.futures import ProcessPoolExecutor
from threading import Timer

import requests

from stem.control import Controller
from stem import Signal

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary

from onionscraper.operators import Operator

class Plugin(Operator):
    """OnionScraper main work logic.

    Handles reading the config file, calling sources, maintaining state and
    sending artifacts to operators.
    """
    def __init__(self, logger, **kwargs):
        self.logger = logger
        self.logger.info('Initializing OnionScanner')
        screenshots = kwargs.pop('screenshots_path', None)
        if screenshots:
            self.screenshots = Path(screenshots)
        else:
            self.screenshots = Path(__file__).parents[1]/'screenshots'
        self.onionscan = kwargs['binpath']
        self.timeout = int(kwargs['timeout'])
        self.proxy = kwargs['socks5']
        self.torControl = kwargs['TorController']
        self.retries = int(kwargs['retries'])
        self.headers ={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:72.0) Gecko/20100101 Firefox/72.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language':'en-US,en;q=0.5',
            'DNT': '1', 'Connection':
            'keep-alive',
            'Upgrade-Insecure-Requests': '1'}


        blacklist = kwargs['blacklist'].split(',')
        self.blacklist = re.compile('|'.join([re.escape(word) for word in blacklist]), re.IGNORECASE)
        keywords = kwargs['interestingKeywords'].split(',')
        self.keywords = re.compile('|'.join([re.escape(word) for word in keywords]), re.IGNORECASE)
        self.session = self.get_tor_session()

    def response(self, status, content, onion):
        """
        status: success/failure
        content: dict
        onion: str
        return: dict
        """
        return {'status': status, 'data': content, 'onion': onion}

    def parseDoc(self, data):
        data['onionscan'].pop('simpleReport', None)
        crawls = data['onionscan'].pop('crawls', None)
        hiddenService = data['onionscan'].pop('hiddenService', None)
        data['onionscan']['crawls'] = [*crawls]
        data['hiddenService'] = hiddenService
        for onion in crawls.keys():
            print(onion)
            #q.enqueue(self.crawl, onion)
        #with open('test.json', 'w', encoding='utf-8') as f:
        #    json.dump(data, f, ensure_ascii=False, indent=4)
        return data

    def format_directory(self, directory):
        d = dt.now()
        year = str(d.year)
        month = str(d.month)
        # prefix month and day with "0" if it is only one digit
        if len(month) < 2:
                month = "0" + month
        day = str(d.day)
        if len(day) < 2:
                day = "0" + day
        save_path = directory/year/month/day
        if not os.path.isdir(save_path):
            self.logger.info("[*] Creating directory to save screenshots")
            os.makedirs(save_path)

        return save_path

    def take_screenshot(self, save_path, onion):
        binary = FirefoxBinary('/home/tony/Projects/OnionScraper/geckodriver')
        fp = webdriver.FirefoxProfile()
        fp.set_preference('network.proxy.type', 1)
        fp.set_preference('network.proxy.socks', '127.0.0.1')
        fp.set_preference('network.proxy.socks_port', 9050)
        fp.set_preference('network.proxy.socks_remote_dns', True)

        options = Options()
        options.headless = True
        driver = webdriver.Firefox(
                executable_path='/home/tony/Projects/OnionScraper/geckodriver',
                options=options,
                firefox_profile=fp)
        url = 'http://' + onion
        driver.get(url)
        uid = str(uuid4()).split('-')[0]
        filename = f"{onion}_screenshot_{uid}.png"
        f_name = f"{save_path}/{filename}"
        driver.save_screenshot(f_name)

        driver.quit()

        if os.path.isfile(f_name):
            self.logger.info(f'[*] Screenshot was taken. {f_name}')
            dateScreenshoted = dt.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')+ 'Z'
            result = {'dateScreenshoted':dateScreenshoted,'filename':filename}
            return self.response("success",result,onion)
        else:
            self.logger.error('[x] Unable to take screenshot')
            return self.response("failure",None,onion)

        
    
    def get_tor_session(self):
        try:
            s = requests.session()
            s.proxies = self.proxy
            s.headers.update(self.headers)
        except Exception as e:
            self.logger.error(e)
            self.logger.debug(traceback.print_exc())
        return s

    # signal TOR for a new connection
    def renew_connection(self):
        with Controller.from_port(port = self.torControl['port']) as controller:
            # Now we switch TOR identities to make sure we have a good connection
            self.logger.info('Getting new Tor IP')
            # authenticate to our local TOR controller
            controller.authenticate(self.torControl['password'])
            # send the signal for a new identity
            controller.signal(Signal.NEWNYM)
            # wait for the new identity to be initialized
            time.sleep(controller.get_newnym_wait())
            session = self.get_tor_session()
            self.logger.info(f"IP is {session.get('http://httpbin.org/ip').json()['origin']}")

    def handle_timeout(self, process, onion):
        #
        # Handle a timeout from the onionscan process.
        #

        try:
            # kill the onionscan process
            process.kill()
            self.logger.info("[!!!] Killed the onionscan process.")
        except:
            pass
        self.renew_connection()
        return

    def run_sessions(self, onion):
            retry = 0
            result = None
            while True:
                try:
                    url = 'http://'+onion
                    self.logger.info(url)
                    content = self.session.get(url)
                    if content.status_code == 200:
                        result = content.json()
                except JSONDecodeError as e:
                    self.logger.debug(f'JSONDecodeError {e}')
                    result = content.text
                except Exception as e:
                    self.logger.error(e)
                    self.logger.debug(traceback.print_exc())
                finally:
                    if result:
                        return self.response("success",result,onion)
                    else:
                        self.logger.info('[x] No results found retrying ...')
                        retry += 1
                        self.renew_connection()
                if retry > self.retries:
                    self.logger.error('[x] Max retries exceeded')
                    return self.response("failure",None, onion)

    def run_onionscan(self, onion):
        self.logger.info("[*] Running onionscan on %s", onion)

        # fire up onionscan
        process = subprocess.Popen([self.onionscan,"--webport=0","--jsonReport","--simpleReport=false",onion],stdout=subprocess.PIPE,stderr=subprocess.PIPE)

        # start the timer and let it run till timeout minutes
        process_timer = Timer(300,self.handle_timeout,args=[process,onion])
        process_timer.start()

        # wait for the onion scan results
        stdout = process.communicate()[0]

        # we have received valid results so we can kill the timer
        if process_timer.is_alive():
            process_timer.cancel()
            return self.response("success",json.loads(stdout),onion)

        self.logger.info("[!!!] Process timed out for %s", onion)

        return self.response("failure",None, onion)

    def handle_onion(self, onion_tuple):
        onion = onion_tuple.url
        self.logger.info(f'Processing {onion} with onionscan')
        try:
            blacklist_URL = self.blacklist.search(onion)
            if blacklist_URL:
                self.logger.info(f"[X] Blocked by blacklist => matched keyword {blacklist_URL.group()}")
            else:
                self.logger.debug("[*] URL blacklist test: PASSED")
                results = self.run_onionscan(onion)
                if results['status'] == 'success' and results['data']['webDetected'] == 'true':
                    content = self.run_sessions(onion)
                    if content['status'] == 'success':
                        blacklist_CONTENT = self.blacklist.search(content['data'])
                        if blacklist_CONTENT:
                            self.logger.info(f"[X] Blocked by blacklist content => matched keyword {blacklist_CONTENT.group()}")
                        else:
                            self.logger.debug("[*] CONTENT blacklist test: PASSED")
                            screenshot = self.take_screenshot(self.format_directory(self.screenshots), onion)
                            self.logger.info("Indexing!")
                            doc = {
                                    'onionscan':json.loads(results['data']),
                                    'html':content['data'],
                                    'screenshots':screenshot['data'],
                                    'interestingKeywords':self.interestingKeywords.findall(content['data'])
                                    }
                            return self.parseDoc(doc)

                else:
                    self.logger.info(f"[x] hidden service {onion} is not active")
        except Exception as e:
            self.logger.error(e)
            self.logger.error(traceback.print_exc())
        finally:
            pass
            #sys.exit(0)

        

