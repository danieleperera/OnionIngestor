import json
import time
import traceback
import subprocess
from threading import Timer
from json.decoder import JSONDecodeError
from concurrent.futures import ProcessPoolExecutor

import requests

from onioningestor.operators import Operator


class Plugin(Operator):
    """OnionScraper main work logic.

    Handles reading the config file, calling sources, maintaining state and
    sending artifacts to operators.
    """
    def __init__(self, logger, **kwargs):
        self.name = kwargs['name']
        self.logger = logger
        self.logger.info(f'Initializing {self.name}')
        self.onionscan = kwargs['binpath']
        self.timeout = int(kwargs.get('timeout', 300))
        self.torControl = 9051
        self.torControl = "Zue5a29v4xE6FciWpPF93rR2M2T"

    def parseDoc(self, data):
        data['onionscan'].pop('simpleReport', None)
        crawls = data['onionscan'].pop('crawls', None)
        hiddenService = data['onionscan'].pop('hiddenService', None)
        data['onionscan']['crawls'] = [*crawls]
        data['hiddenService'] = hiddenService
        for onion in crawls.keys():
            self.queueCrawl((
                3,
                self.onion(
                    url=onion,
                    source='crawled',
                    type='domain',
                    status='offline',
                    monitor=False,
                    denylist=False)))
        return data

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
            self.logger.info(f"IP is {requests.get('http://httpbin.org/ip').json()['origin']}")

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

    def run_onionscan(self, onion):
        self.logger.info("[*] Running onionscan on %s", onion)

        # fire up onionscan
        process = subprocess.Popen([self.onionscan,"--webport=0","--jsonReport","--simpleReport=false",onion],stdout=subprocess.PIPE,stderr=subprocess.PIPE)

        # start the timer and let it run till timeout minutes
        process_timer = Timer(self.timeout,self.handle_timeout,args=[process,onion])
        process_timer.start()

        # wait for the onion scan results
        stdout = process.communicate()[0]

        # we have received valid results so we can kill the timer
        if process_timer.is_alive():
            process_timer.cancel()
            try:
                return self.response(
                        "success",
                        self.parseDoc(json.loads(stdout)))
            except json.decoder.JSONDecodeError:
                return self.response(
                        "success",
                        self.parseDoc(stdout))

        self.logger.info("[!!!] Process timed out for %s", onion)
        return self.response("failed",stdout)

    def handle_onion(self, onion):
        try:
            results = self.run_onionscan(onion.url)
            onion.onionscan(results)
        except Exception as e:
            self.logger.error(e)
            self.logger.error(traceback.print_exc())
        finally:
            pass
