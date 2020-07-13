import io
import importlib
import traceback

import yaml

from pathlib import Path


SOURCE = "onioningestor.sources"
OPERATOR = "onioningestor.operators"
INTERNAL_OPTIONS = [
    "saved_state",
    "module",
    "credentials",
]
ARTIFACT_TYPES = "artifact_types"
FILTER_STRING = "filter"
ALLOWED_SOURCES = "allowed_sources"
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
            print(e)
            print(traceback.print_exc())

    def daemon(self):
        """Returns boolean, are we daemonizing?"""
        return self.config["general"]["daemon"]

    def elasticsearch(self):
        """Returns elasticsaerch config"""
        return self.config["general"]["elasticsearch"]

    def sleep(self):
        """Returns number of seconds to sleep between iterations, if daemonizing."""
        return self.config["general"]["sleep"]

    def blacklist(self):
        return self.config["general"]["blacklist"].split(",")

    #    def onionscanner(self):
    #        """Returns onionscanner config dict"""
    #        screenshots = self.config['onionscanner'].pop('screenshots_path', None)
    #        if screenshots:
    #            self.config['onionscanner']['screenshots_path'] = Path(screenshots)
    #        else:
    #            self.config['onionscanner']['screenshots_path'] = Path(__file__).parents[1]/'screenshots'
    #        blacklist = self.config['onionscanner'].pop('blacklist', None)
    #        if blacklist:
    #            self.config['onionscanner']['blacklist'] = blacklist.split(',')
    #        interestingKeywords = self.config['onionscanner'].pop('interestingKeywords', None)
    #        if interestingKeywords:
    #            self.config['onionscanner']['interestingKeywords'] = blacklist.split(',')
    #        return self.config['onionscanner']

    def notifiers(self):
        """Returns notifiers config dictionary."""
        return self.config.get("notifiers", {})

    def logging(self):
        """Returns logging config dictionary."""
        return self.config.get("logging", {})

    def credentials(self, credential_name):
        """Return a dictionary with the specified credentials."""
        for credential in self.config["credentials"]:
            for key, value in credential.items():
                if key == NAME and value == credential_name:
                    return credential
        return {}

    def sources(self):
        """Return a list of (name, Source class, {kwargs}) tuples.
        :raises: threatingestor.exceptions.PluginError
        """
        sources = []

        for source in self.config["sources"]:
            kwargs = {}
            for key, value in source.items():
                if key not in INTERNAL_OPTIONS:
                    kwargs[key] = value

                elif key == "credentials":
                    # Grab these named credentials
                    credential_name = value
                    for credential_key, credential_value in self.credentials(
                        credential_name
                    ).items():
                        if credential_key != NAME:
                            kwargs[credential_key] = credential_value

            # load and initialize the plugin
            self.logger.info(f"Found source '{source[NAME]}'")
            sources.append(
                (source[NAME], self._load_plugin(SOURCE, source["module"]), kwargs)
            )

        self.logger.info(f"Found {len(sources)} total sources")
        return sources

    def operators(self):
        """Return a list of (name, Operator class, {kwargs}) tuples.
        :raises: threatingestor.exceptions.PluginError
        """
        operators = []
        for operator in self.config["operators"]:
            kwargs = {}
            for key, value in operator.items():
                if key not in INTERNAL_OPTIONS:
                    if key == ARTIFACT_TYPES:
                        # parse out special artifact_types option
                        artifact_types = []
                        for artifact in value:
                            try:
                                artifact_types.append(
                                    threatingestor.artifacts.STRING_MAP[
                                        artifact.lower().strip()
                                    ]
                                )
                            except KeyError:
                                # ignore invalid artifact types
                                pass
                        kwargs[key] = artifact_types

                    elif key == FILTER_STRING:
                        # pass in special filter_string option
                        kwargs["filter_string"] = value

                    elif key == NAME:
                        # exclude name key from operator kwargs, since it's not used
                        pass

                    else:
                        kwargs[key] = value

                elif key == "credentials":
                    # Grab these named credentials
                    credential_name = value
                    for credential_key, credential_value in self.credentials(
                        credential_name
                    ).items():
                        if credential_key != NAME:
                            kwargs[credential_key] = credential_value

            # load and initialize the plugin
            self.logger.info(f"Found operator '{operator[NAME]}'")
            operators.append(
                (
                    operator[NAME],
                    self._load_plugin(OPERATOR, operator["module"]),
                    kwargs,
                )
            )

        self.logger.info(f"Found {len(operators)} total operators")
        return operators
