import sys
import traceback

from elasticsearch import Elasticsearch, helpers

class DbHandlerElasticSearch:
    def __init__(self, config, logger):
        self.logger = logger
        self.logger.info('Creating Elasticsearch mapping')
        self.config = config
        self.mapping = '''
        {
          "mappings": {
            "_doc": {
              "properties": {
                "hiddenService": {
                  "type": "text"
                },
                "blacklist": {
                  "type": "keyword"
                },      
                "monitor": {
                  "type": "boolean"
                },
                "simple-html": {
                  "type": "nested",
                  "properties": {
                    "HTML": {
                      "type": "long"
                    },
                    "title": {
                      "type": "text"
                    },
                    "language": {
                      "type": "text"
                    },
                    "status":{
                      "type":"text"
                    },
                    "date-indexed": {
                      "type": "date"
                    }
                  }
                }
              }
            }
          }
        }
        '''
        self.index = self.config['index']
        try:
            self.es = Elasticsearch([{
                'host':self.config['host'],
                'port':self.config['port']}])
            self.es.indices.create(
                    index=self.index,
                    body=self.mapping,
                    ignore=400)
        except Exception as e:
            self.logger.error(e)
            self.logger.error(traceback.format_exc())
            sys.exit(0)

    def count(self):
        self.es.indices.refresh(self.index)
        status = self.es.count(index=self.index)
        if status['_shards']['successful'] == 1:
            self.logger.info('Successful')
            self.logger.info('Count:%d',status['count'])
        else:
            self.logger.error(status)

    def save(self, doc):
        self.es.index(index=self.index,body=doc)
        self.count()
