import re
import sys
import json
import time
import requests
from queue import Queue
from datetime import datetime as dt
from concurrent.futures import ThreadPoolExecutor

from stem.control import Controller
from stem import Signal

from onioningestor.onion import Onion

class Operator:
    """Base class for all Operator plugins.

    Note: This is an abstract class. You must extend ``__init__`` and call
    ``super`` to ensure this class's constructor is called. You must override
    ``handle_artifact`` with the same signature. You may define additional
    ``handle_{artifact_type}`` methods as needed (see the threatkb operator for
    an example) - these methods are purely convention, and are not required.

    When adding additional methods to child classes, consider prefixing the
    method name with an underscore to denote a ``_private_method``. Do not
    override other existing methods from this class.
    """
    
    def __init__(self, logger, config, allowed_sources=None):
        """Override this constructor in child classes.

        The arguments above (artifact_types, filter_string, allowed_sources)
        should be accepted explicity as above, in all child classes.

        Additional arguments should be added: url, auth, etc, whatever is
        needed to set up the object.

        Each operator should default self.artifact_types to a list of Artifacts
        supported by the plugin, and allow passing in artifact_types to
        overwrite that default.

        Example:

        >>> self.artifact_types = artifact_types or [
        ...     artifacts.IPAddress,
        ...     artifacts.Domain,
        ... ]

        It's recommended to call this __init__ method via super from all child
        classes. Remember to do so *before* setting any default artifact_types.
        """
        self.logger = logger
        self.onion = Onion
        self.torControl = config
        deny = allowed_sources or []
        self.blacklist = re.compile('|'.join([re.escape(word) for word in deny]), re.IGNORECASE)

    # signal TOR for a new connection
    def renew_connection(self):
        with Controller.from_port(port = int(self.torControl['port'])) as controller:
            # Now we switch TOR identities to make sure we have a good connection
            self.logger.info('Getting new Tor IP')
            # authenticate to our local TOR controller
            controller.authenticate(self.torControl['password'])
            # send the signal for a new identity
            controller.signal(Signal.NEWNYM)
            # wait for the new identity to be initialized
            time.sleep(controller.get_newnym_wait())
            self.logger.info(f"IP is {requests.get('http://httpbin.org/ip').json()['origin']}")

    def set_crawlQueue(self, queue):
        self.queueCrawl = queue

    def handle_onion(self, url):
        """Override with the same signature.

        :param artifact: A single ``Artifact`` object.
        :returns: None (always ignored)
        """
        raise NotImplementedError()

    def response(self, operator, status, content):
        """
        status: success/failure
        content: dict
        onion: str
        return: dict
        """
        try:
            return {operator:{'status':status, 'content': content}}
        except Exception as e:
            self.logger.error(e)

    def _onion_is_allowed(self, content, onion):
        """Returns True if this is allowed by this plugin's filters."""
        blacklist = self.blacklist.findall(content)
        if blacklist:
            onion.denylist = blacklist
            onion.status = 'blocked'

    def findCrawls(self, content, hiddenService):
        crawl = set()
        for onion in re.findall(r'\s?(\w+.onion)', str(content)):
            if onion != hiddenService:
                crawl.add(onion)
        for item in crawl:
            self.logger.debug(f'crawling queue added: {item}')
            self.queueCrawl.put((
                3,
                self.onion(
                    url=item,
                    source='crawled',
                    type='domain',
                    status='offline',
                    monitor=False,
                    denylist=False)))

    def process(self, onion):
        """Process all applicable onions."""
        self.handle_onion(onion[1])
        #with ThreadPoolExecutor(max_workers=1) as executor:
        #    collect_tasks = [executor.submit(self.collect, files_batch) for files_batch in self.iter_batches(onions, batch_size=10)]
        #    for tasks in collect_tasks:
        #        self.logger.info(tasks.result())
