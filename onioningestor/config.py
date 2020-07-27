import io
import importlib
import traceback
from queue import PriorityQueue
from collections import namedtuple
import yaml

from pathlib import Path

from onioningestor.onion import Onion

SOURCE = "onioningestor.sources"
OPERATOR = "onioningestor.operators"
DATABASE_ENGINE = "onioningestor.databases"

NAME = "name"


class Config:
    """Config read/write operations, and convenience methods."""

    def __init__(self, filename, logger):
        """Read a config file."""
        self.logger = logger
        self.filename = filename
        with io.open(self.filename, "r") as f:
            try:
                self.logger.info("Loading config file")
                self.config = yaml.safe_load(f.read())
            except yaml.error.YAMLError:
                self.logger.error("YAML error in config")

    @staticmethod
    def _load_plugin(plugin_type, plugin):
        """Returns plugin class or raises an exception.
        :raises: threatingestor.exceptions.PluginError
        """
        try:
            module = importlib.import_module(".".join([plugin_type, plugin]))
            return module.Plugin
        except Exception as e:
            self.logger.error(e)
            self.logger.debug(traceback.print_exc())

    def daemon(self):
        """Returns boolean, are we daemonizing?"""
        return self.config["general"]["daemon"]

    def save_thread(self):
        return self.config["general"].get("save-thread", False)

    def sleep(self):
        """Returns number of seconds to sleep between iterations, if daemonizing."""
        return self.config["general"]["sleep"]

    def blacklist(self):
        return self.config["general"]["blacklist"].split(",")

    def torController(self):
        return self.config["general"]["TorController"]

    def monitorQueue(self):
        fp = Path(self.config["monitor"].get("filename", "this_File_Does_notExsit"))
        q = PriorityQueue(maxsize=0)
        if fp.is_file():
            with open(fp, 'r') as f:
                monitorOnions = f.read().splitlines()
            for monitor in monitorOnions:
                q.put((
                    1,
                    Onion(
                    url=monitor,
                    source='monitor',
                    type='domain',
                    status='offline',
                    monitor=True,
                    denylist=False)))
            return q
        else:
            return q

    def logging(self):
        """Returns logging config dictionary."""
        return self.config.get("logging", {})

    def database_engines(self):
        """Return a list of (name, Source class, {kwargs}) tuples.
        :raises: threatingestor.exceptions.PluginError
        """
        engines = []

        for engine in self.config["database_Engines"]:
            kwargs = {}
            for key, value in engine.items():
                kwargs[key] = value
            # load and initialize the plugin
            self.logger.debug(f"Found database engine '{engine[NAME]}'")
            kwargs.pop('module',None)
            engines.append(
                    (
                    engine[NAME],
                    self._load_plugin(DATABASE_ENGINE, engine["module"]),
                    kwargs
                    )
            )

        self.logger.debug(f"Found {len(engines)} total database engines")
        return engines

    def sources(self):
        """Return a list of (name, Source class, {kwargs}) tuples.
        :raises: threatingestor.exceptions.PluginError
        """
        sources = []

        for source in self.config["sources"]:
            kwargs = {}
            for key, value in source.items():
                kwargs[key] = value
            # load and initialize the plugin
            self.logger.debug(f"Found source '{source[NAME]}'")
            kwargs.pop('module',None)
            sources.append(
                    (
                    source[NAME],
                    self._load_plugin(SOURCE, source["module"]),
                    kwargs
                    )
            )

        self.logger.debug(f"Found {len(sources)} total sources")
        return sources

    def operators(self):
        """Return a list of (name, Operator class, {kwargs}) tuples.
        :raises: threatingestor.exceptions.PluginError
        """
        operators = []
        for operator in self.config["operators"]:
            kwargs = {}
            for key, value in operator.items():
                kwargs[key] = value
            # load and initialize the plugin
            self.logger.debug(f"Found operator '{operator[NAME]}'")
            kwargs.pop('module',None)
            operators.append(
                (
                    operator[NAME],
                    self._load_plugin(OPERATOR, operator["module"]),
                    kwargs,
                )
            )

        self.logger.debug(f"Found {len(operators)} total operators")
        return operators
