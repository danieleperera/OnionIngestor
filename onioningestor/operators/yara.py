
from onionscraper.operators import Operator


class Plugin(Operator):
    """Operator for output to flat CSV file."""
    def __init__(self, filename, base_score):
        """CSV operator."""
        self.filename = filename

        #super(Plugin, self).__init__(artifact_types, filter_string, allowed_sources)


    def handle_artifact(self, artifact):
        """Operate on a single artifact."""
        pass
