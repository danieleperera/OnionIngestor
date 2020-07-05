from collections import namedtuple

class Source(object):
    """Base class for all Source plugins.
    Note: This is an abstract class. You must override ``__init__`` and ``run``
    in child classes. You should not override ``process_element``. When adding
    additional methods to child classes, consider prefixing the method name
    with an underscore to denote a ``_private_method``.
    """
    def __init__(self, name, *args, **kwargs):
        """Override this constructor in child classes.
        The first argument must always be ``name``.
        Other argumentss should be url, auth, etc, whatever is needed to set
        up the object.
        """
        self.onion = namedtuple('onion', ['url','source','type'])


    def run(self):
        """Run and return ``(saved_state, list(Artifact))``.
        Override this method in child classes.
        The method signature and return values must remain consistent.
        The method should attempt to pick up where we left off using
        ``saved_state``, if supported. If ``saved_state`` is ``None``, you can
        assume this is a first run. If state is maintained by the remote
        resource (e.g. as it is with SQS), ``saved_state`` should always be
        ``None``.
        """
        raise NotImplementedError()


    def process_element(self, content, reference_link, include_nonobfuscated=False):
        """Take a single source content/url and return a list of Artifacts.
        This is the main work block of Source plugins, which handles
        IOC extraction and artifact creation.
        :param content: String content to extract from.
        :param reference_link: Reference link to attach to all artifacts.
        :param include_nonobfuscated: Include non-defanged URLs in output?
        """
        logger.debug(f"Processing in source '{self.name}'")

