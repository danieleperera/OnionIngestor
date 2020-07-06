import os
import logging
from pathlib import Path

class LoggerHandler():
    def __init__(self, level):
        self.level = getattr(logging, level)
        self.logger = logging.getLogger("OnionScraper")
        self.logger.setLevel(self.level)

        # create console handler and set level to debug
        ch = logging.StreamHandler()
        ch.setLevel(self.level)

        # create file logging
        logFile = Path(__file__).parents[1]
        logging_path = os.path.join(logFile, "info.log")
        fh = logging.FileHandler(logging_path)

        # create formatter
        formatter = logging.Formatter('[%(asctime)s] - %(name)s - %(levelname)s - %(message)s',datefmt='%a, %d %b %Y %H:%M:%S')
        formatter_console = logging.Formatter('[%(asctime)s] - %(levelname)s - %(message)s',datefmt='%d %b %Y %H:%M:%S')
        # add formatter to ch
        ch.setFormatter(formatter_console)
        fh.setFormatter(formatter)
        # add ch to logger
        self.logger.addHandler(ch)  #added logging into console
        self.logger.addHandler(fh)  #added logging into file

    def start_logging(self):
        self.logger.info('Starting OnionScraper')
        return self.logger

