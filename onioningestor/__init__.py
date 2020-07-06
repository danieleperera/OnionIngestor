import sys
import time
import traceback
import collections

from . import config
from . import dbhandler
from . import loghandler


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

        # Load Elasticsearch.
        try:
            self.es = dbhandler.DbHandlerElasticSearch(
                    self.config.elasticsearch(),
                    self.logger)
        except Exception as e:
            # Error loading elasticsearch.
            self.logger.error(e)
            self.logger.debug(traceback.print_exc())
            sys.exit(1)


        # Instantiate plugins.
        try:
            self.logger.info("Initializing sources")
            self.sources = {name: source(self.logger, **kwargs)
                            for name, source, kwargs in self.config.sources()}

            self.logger.info("initializing operators")
            self.operators = {name: operator(self.logger, self.es, self.blacklist, **kwargs)
                              for name, operator, kwargs in self.config.operators()}

            self.logger.info("initializing notifiers")
            #self.notifiers = {name: operator(**kwargs)
            #                  for name, operator, kwargs in self.config.notifiers()}
        except Exception as e:
            # Error loading elasticsearch.
            self.logger.error(e)
            self.logger.debug(traceback.print_exc())
            sys.exit(1)


    def run(self):
        """Run once, or forever, depending on config."""
        if self.config.daemon():
            self.logger.info("Running forever, in a loop")
            self.run_forever()
        else:
            self.logger.info("Running once, to completion")
            self.run_once()


    def run_once(self):
        """Run each source once, passing artifacts to each operator."""
        # Track some statistics about artifacts in a summary object.
        summary = collections.Counter()

        for source in self.sources:
            # Run the source to collect artifacts.
            self.logger.info(f"Running source '{source}'")
            try:
                onions = self.sources[source].run()
                if onions:
                    self.logger.info(f'Found hidden links')
                else:
                    self.logger.info('No links found')
            except Exception as e:
                self.logger.error(e)
                self.logger.error(traceback.print_exc())
                continue

            # Process artifacts with each operator.
            for operator in self.operators:
                self.logger.info(f"Processing found onions with operator '{operator}'")
                try:
                    doc = self.operators[operator].process(onions)
                    # Save the source state.
                    self.es.save(doc)
                except Exception as e:
                    self.logger.error(e)
                    self.logger.error(traceback.print_exc())
                    continue



#            # Record stats and update the summary.
#            types = artifact_types(doc.get('interestingKeywords'))
#            summary.update(types)
#            for artifact_type in types:
#                self.logger.info(f'types[artifact_type]')

        # Log the summary.
        self.logger.info(f"New artifacts: {dict(summary)}")


    def run_forever(self):
        """Run forever, sleeping for the configured interval between each run."""
        while True:
            self.run_once()

            self.logger.info(f"Sleeping for {self.config.sleep()} seconds")
            time.sleep(self.config.sleep())


def artifact_types(artifact_list):
    """Return a dictionary with counts of each artifact type."""
    types = {}
    for artifact in artifact_list:
        artifact_type = artifact.__class__.__name__.lower()
        if artifact_type in types:
            types[artifact_type] += 1
        else:
            types[artifact_type] = 1

    return types


