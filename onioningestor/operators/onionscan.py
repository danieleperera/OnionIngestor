import json
import traceback
import subprocess
from threading import Timer
from json.decoder import JSONDecodeError
from concurrent.futures import ProcessPoolExecutor

import requests

from stem.control import Controller
from stem import Signal


from onioningestor.operators import Operator


class Plugin(Operator):
    """OnionScraper main work logic.

    Handles reading the config file, calling sources, maintaining state and
    sending artifacts to operators.
    """
    def __init__(self, logger, denylist, config, **kwargs):
        super(Plugin, self).__init__(logger, denylist, config)
        self.name = kwargs['name']
        self.logger = logger
        self.logger.info(f'Initializing {self.name}')
        self.onionscan = kwargs['binpath']
        self.timeout = int(kwargs.get('timeout', 300))

    def parseDoc(self, data):
        data.pop('simpleReport', None)
        crawls = data.pop('crawls', None)
        hiddenService = data.pop('hiddenService', None)
        data['crawls'] = [*crawls]
        try:
            if data['identifierReport'].get('linkedOnions', False):
                self.findCrawls(data['identifierReport']['linkedOnions'], hiddenService)
        except KeyError as e:
            pass
        return data


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
                        self.name,
                        "success",
                        self.parseDoc(json.loads(stdout)))
            except json.decoder.JSONDecodeError:
                return self.response(
                        self.name,
                        "success",
                        self.parseDoc(stdout))

        self.logger.info("[!!!] Process timed out for %s", onion)
        return self.response(self.name,"failed", None)

    def handle_onion(self, onion):
        try:
            if onion.status != 'inactive':
                results = self.run_onionscan(onion.url)
                onion.set_operator(results)
        except Exception as e:
            self.logger.error(e)
            self.logger.error(traceback.print_exc())
        finally:
            pass
