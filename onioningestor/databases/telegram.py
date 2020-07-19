import sys
import requests

from onioningestor.databases import PastieStorage

class Plugin(PastieStorage):

    def __init__(self, logger, **kwargs):
        # kwargs = {'name': 'telegram-notifer', 'chat_id': 111111, 'token': 'XXXX'}
        self.name = kwargs.get('name')
        self.logger = logger
        self.token = kwargs.get('token')
        self.chat_id = kwargs.get('chat_id')

    def __save_pastie__(self, pastie):
        message = '''
HiddenSite:        {site}
Source    :        {url}
Monitor   :        {content}
Status    :        {status}        
    '''.format(
            site=pastie.url,
            url=pastie.source,
            content=pastie.monitor,
            status=pastie.status)

        url = 'https://api.telegram.org/bot{0}/sendMessage'.format(self.token)
        try:
            self.logger.debug('Sending message to telegram {} for pastie_id {}'.format(url, pastie))
            requests.post(url, data={'chat_id': self.chat_id, 'text':message})
        except Exception as e:
            self.logger.warning("Failed to alert through telegram: {0}".format(e))

