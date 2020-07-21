import sys
import time
import queue
import traceback
import threading
import collections
from queue import Queue
from itertools import islice

from . import config
from . import loghandler

from onioningestor.databases import StorageDispatcher, StorageThread, StorageSync

class Ingestor:
    """ThreatIngestor main work logic.

    Handles reading the config file, calling sources, maintaining state, and
    sending artifacts to operators.
    """
    def __init__(self, args):
        # Load logger
        log = loghandler.LoggerHandler(args.logLevel)
        self.logger = log.start_logging()
        
        # Load config
        self.config = config.Config(args.configFile, self.logger)
        self.blacklist = self.config.blacklist()

        # Create Queues
        self.queue = self.config.monitorQueue()

        # Get asynchronously o synchronously save
        self.save_thread = self.config.save_thread()

        # Track some statistics about artifacts in a summary object.
        self.summary = collections.Counter()

        # Threads
        self.threads = []
        try:
            # Load Storage Engines - ElasticSearch, Telegram, Twitter etc
            self.storage = StorageDispatcher(self.logger)

            for name, db, kwargs in self.config.database_engines():
                # start the threads handling database storage if needed
                if self.save_thread:
                    self.logger.debug(f"Starting daemon thread for {str(db)}")
                    t = StorageThread(db(self.logger, **kwargs))
                    self.threads.append(t)
                    t.setDaemon(True)
                    t.start()
                # save onions synchronously
                else:
                    s = StorageSync(db(self.logger, **kwargs))
                    self.storage.add_storage(s)

            if self.save_thread:
                self.logger.info("Onions will be saved asynchronously")
            else:
                self.logger.info("Onions will be saved synchronously")

            # Instantiate operator plugins.
            self.logger.debug("initializing operators")
            self.operators = {name: operator(self.logger, self.config.torController(), self.blacklist, **kwargs)
                              for name, operator, kwargs in self.config.operators()}

        except Exception as e:
            # Error loading starting plugins.
            self.logger.error(e)
            self.logger.debug(traceback.print_exc())
            sys.exit(1)

    def iter_batches(self, data, batch_size):
        data = iter(data)
        while True:
            batch = list(islice(data, batch_size))
            if len(batch) == 0:
                break
            yield batch
    
    def process(self, onions):
        for operator in self.operators:
            self.logger.info(f"Processing found onions with operator '{operator}'")
            # Set CrawlQueue for every operator
            self.operators[operator].set_crawlQueue(self.queue)
            # Process list of onions
            self.operators[operator].process(onions)

    def run(self):
        """Run once, or forever, depending on config."""
        self.run_once()
        #if self.config.daemon():
        #    self.logger.info("Running forever, in a loop")
        #    self.run_forever()
        #else:
        #    self.logger.info("Running once, to completion")
        #    self.run_once()


    def run_once(self):
        """Run each source once, passing artifacts to each operator."""
        # Start collecting sources
        self.collect_sources()
        # Sources will fill various queues 
        # MonitorQueue has priority high
        # OnionQueue are those found in clearnet medium
        # crawlQueue are those found crawling onionlinks low
        onions = list(self.queue.queue)
        done = False
        if onions:
            while not done:
                try:
                    ## Process onions with each operator.
                    for batched_onions in self.iter_batches(onions, batch_size=10):
                        self.process(batched_onions)
                        ## Save Onions for each storage
                        for onion in batched_onions:
                            self.storage.save_pastie(onion[1], 30)
                    done = True
                except Exception as e:
                    self.logger.error(e)
                    self.logger.error(traceback.print_exc())
                    break
                except KeyboardInterrupt:
                    print('')
                    self.logger.info("Ctrl-c received! Sending kill to threads...")
                    for t in self.threads:
                        t.kill_received = True
                    self.logger.info('Exiting')
                    sys.exit(0)
        else:
            for t in self.threads:
                t.kill_received = True
            self.logger.info(f"Sleeping for {self.config.sleep()} seconds")
            time.sleep(self.config.sleep())


    def run_forever(self):
        """Run forever, sleeping for the configured interval between each run."""
        while True:
            self.run_once()


    def collect_sources(self):
        self.logger.debug("Initializing sources")
        for name, collect, kwargs in self.config.sources():
            # Run the source to collect onion links from clear net.
            self.logger.info(f"Running source '{name}'")
            try:
                # get the generator of onions
                source = collect(self.logger, **kwargs)
                source.set_onionQueue(self.queue) #priority 2
                t = source.run()
                self.threads.append(t)
                #self.logger.info(f'Starting of thread: {t.currentThread().name}')
                #t.start()
            except Exception as e:
                self.logger.error(e)
                self.logger.error(traceback.print_exc())
                continue

