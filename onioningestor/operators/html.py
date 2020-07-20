import re
import time
import json
import traceback
from datetime import datetime as dt
from json.decoder import JSONDecodeError
from collections import Counter

import requests

from bs4 import BeautifulSoup

from langdetect import detect

from stem.control import Controller
from stem import Signal

from onioningestor.operators import Operator


class Plugin(Operator):
    """Simple-html
    This plugin collects HTML code from onion link
    """

    def __init__(self, logger, denylist, **kwargs):
        super(Plugin, self).__init__(logger, denylist)
        self.name = kwargs['name']
        self.logger.info(f"Initializing {self.name}")

        self.timeout = int(kwargs["timeout"])
        self.retries = int(kwargs["retries"])

        interesting = kwargs["interestingKeywords"].split(",")
        self.interesting = re.compile(
            "|".join([re.escape(word) for word in interesting]), re.IGNORECASE
        )

        self.proxy = kwargs["socks5"]
        self.torControl = kwargs["TorController"]
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:72.0) Gecko/20100101 Firefox/72.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }

    def get_tor_session(self):
        try:
            s = requests.session()
            s.proxies = self.proxy
            s.headers.update(self.headers)
        except Exception as e:
            self.logger.error(e)
            self.logger.debug(traceback.print_exc())
        return s

    def renew_connection(self):
        with Controller.from_port(port=self.torControl["port"]) as controller:
            # Now we switch TOR identities to make sure we have a good connection
            self.logger.info("Getting new Tor IP")
            # authenticate to our local TOR controller
            controller.authenticate(self.torControl["password"])
            # send the signal for a new identity
            controller.signal(Signal.NEWNYM)
            # wait for the new identity to be initialized
            time.sleep(controller.get_newnym_wait())
            session = self.get_tor_session()
            self.logger.info(
                f"IP is {session.get('http://httpbin.org/ip').json()['origin']}"
            )

    def run_sessions(self, onion):
        retry = 0
        result = None
        while True:
            try:
                url = "http://" + onion
                self.logger.info(url)
                content = self.get_tor_session().get(url)
                if content.status_code == 200:
                    result = content.text
                    if result:
                        html = BeautifulSoup(result, features="lxml")
                        if html:
                            index = {
                                "HTML": result,
                                "title": html.title.text,
                                "language": detect(html.text),
                                "status": "success",
                                "interestingKeywords": list(set(self.interesting.findall(result))),
                            }
                        else:
                            index = {
                                "HTML": result,
                                "title": None,
                                "language": None,
                                "status": "success",
                                "interestingKeywords": list(set(self.interesting.findall(result))),
                            }
                        return self.response("success", index)

            except requests.exceptions.ConnectionError as connection_error:
                self.logger.error(f"Failed connecting to http://{url}")
                self.logger.debug(connection_error)
            except Exception as e:
                self.logger.error(e)
                self.logger.debug(traceback.print_exc())

            self.logger.info("[x] No results found retrying ...")
            retry += 1
            self.renew_connection()
            if retry > self.retries:
                self.logger.error("[x] Max retries exceeded")
                return self.response("failed", None)

    def handle_onion(self, onion):
        html = self.run_sessions(onion.url)
        if html['status'] == 'success':
            self._onion_is_allowed(html['content']['HTML'], onion)
        onion.simpleHTML(html)
