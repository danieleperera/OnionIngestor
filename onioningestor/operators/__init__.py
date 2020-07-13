import re
import sys
import json
from itertools import islice
from datetime import datetime as dt
from concurrent.futures import ThreadPoolExecutor


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
    
    def __init__(self, logger, elasticsearch, allowed_sources=None):
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
        self.blacklist = re.compile('|'.join([re.escape(word) for word in allowed_sources]), re.IGNORECASE)
        self.es = elasticsearch

    def response(self, content, onion, operator_name):
        """
        status: success/failure
        content: dict
        onion: str
        return: dict
        """
        try:
            return {operator_name: content, 'hiddenService': onion}
        #except TypeError:
        #    return {operator_name: None, 'hiddenService': onion}
        except Exception as e:
            self.logger.error(e)

    def handle_onion(self, db, url):
        """Override with the same signature.

        :param artifact: A single ``Artifact`` object.
        :returns: None (always ignored)
        """
        raise NotImplementedError()


    def _onion_is_allowed(self, response, db, type='URL'):
        """Returns True if this is allowed by this plugin's filters."""
        # Must be in allowed_sources, if set.
        if type == 'URL':
            blacklist = self.blacklist.findall(response['hiddenService'])
        elif type == 'HTML':
            blacklist = self.blacklist.findall(response['simple-html']['HTML'])
        if blacklist:
            response['simple-html'].pop('status')
            response['simple-html']['status'] = 'blocked'
            response['blacklist'] = list(set(blacklist))
            self.es.update(db['_id'], response)
            return False
        return True

    def collect(self, onions):
        for onion in onions:
            self.logger.info(f'thread function processing {onion}')
            # Add link to database
            db = self.es.save({
                'hiddenService':onion.url,
                'monitor':'false',
                'dateAdded':dt.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')+ 'Z'})
            if self._onion_is_allowed(
                    self.response({'status':'blocked'},onion.url,'regex-blacklist'),
                    db,
                    type='URL'):
                # Get data for current link
                self.handle_onion(db, onion.url)

    def iter_batches(self, data, batch_size):
        data = iter(data)
        while True:
            batch = list(islice(data, batch_size))
            if len(batch) == 0:
                break
            yield batch

    def process(self, onions):
        """Process all applicable onions."""
        #print(onions)
        with ThreadPoolExecutor(max_workers=10) as executor:
            collect_tasks = [executor.submit(self.collect, files_batch) for files_batch in self.iter_batches(onions, batch_size=10)]
            for tasks in collect_tasks:
                self.logger.info(tasks.result())
