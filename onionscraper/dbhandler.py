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
        "html": {
          "type": "text"
        },
        "onionscan": {
          "type": "nested",
          "properties": {
            "bitcoinDetected": {
              "type": "boolean"
            },
            "bitcoinServices": {
              "properties": {
                "bitcoin": {
                  "properties": {
                    "detected": {
                      "type": "boolean"
                    },
                    "prototocolVersion": {
                      "type": "long"
                    },
                    "userAgent": {
                      "type": "text",
                      "fields": {
                        "keyword": {
                          "type": "keyword",
                          "ignore_above": 256
                        }
                      }
                    }
                  }
                },
                "bitcoin_test": {
                  "properties": {
                    "detected": {
                      "type": "boolean"
                    },
                    "prototocolVersion": {
                      "type": "long"
                    },
                    "userAgent": {
                      "type": "text",
                      "fields": {
                        "keyword": {
                          "type": "keyword",
                          "ignore_above": 256
                        }
                      }
                    }
                  }
                },
                "dogecoin": {
                  "properties": {
                    "detected": {
                      "type": "boolean"
                    },
                    "prototocolVersion": {
                      "type": "long"
                    },
                    "userAgent": {
                      "type": "text",
                      "fields": {
                        "keyword": {
                          "type": "keyword",
                          "ignore_above": 256
                        }
                      }
                    }
                  }
                },
                "litecoin": {
                  "properties": {
                    "detected": {
                      "type": "boolean"
                    },
                    "prototocolVersion": {
                      "type": "long"
                    },
                    "userAgent": {
                      "type": "text",
                      "fields": {
                        "keyword": {
                          "type": "keyword",
                          "ignore_above": 256
                        }
                      }
                    }
                  }
                }
              }
            },
            "certificates": {
              "type": "nested",
              "properties": {
                "AuthorityKeyId": {
                  "type": "text",
                  "fields": {
                    "keyword": {
                      "type": "keyword",
                      "ignore_above": 256
                    }
                  }
                },
                "BasicConstraintsValid": {
                  "type": "boolean"
                },
                "CRLDistributionPoints": {
                  "type": "text",
                  "fields": {
                    "keyword": {
                      "type": "keyword",
                      "ignore_above": 256
                    }
                  }
                },
                "DNSNames": {
                  "type": "text",
                  "fields": {
                    "keyword": {
                      "type": "keyword",
                      "ignore_above": 256
                    }
                  }
                },
                "ExtKeyUsage": {
                  "type": "long"
                },
                "Extensions": {
                  "properties": {
                    "Critical": {
                      "type": "boolean"
                    },
                    "Id": {
                      "type": "long"
                    },
                    "Value": {
                      "type": "text",
                      "fields": {
                        "keyword": {
                          "type": "keyword",
                          "ignore_above": 256
                        }
                      }
                    }
                  }
                },
                "IsCA": {
                  "type": "boolean"
                },
                "Issuer": {
                  "properties": {
                    "CommonName": {
                      "type": "text",
                      "fields": {
                        "keyword": {
                          "type": "keyword",
                          "ignore_above": 256
                        }
                      }
                    },
                    "Country": {
                      "type": "text",
                      "fields": {
                        "keyword": {
                          "type": "keyword",
                          "ignore_above": 256
                        }
                      }
                    },
                    "Locality": {
                      "type": "text",
                      "fields": {
                        "keyword": {
                          "type": "keyword",
                          "ignore_above": 256
                        }
                      }
                    },
                    "Names": {
                      "properties": {
                        "Type": {
                          "type": "long"
                        },
                        "Value": {
                          "type": "text",
                          "fields": {
                            "keyword": {
                              "type": "keyword",
                              "ignore_above": 256
                            }
                          }
                        }
                      }
                    },
                    "Organization": {
                      "type": "text",
                      "fields": {
                        "keyword": {
                          "type": "keyword",
                          "ignore_above": 256
                        }
                      }
                    },
                    "OrganizationalUnit": {
                      "type": "text",
                      "fields": {
                        "keyword": {
                          "type": "keyword",
                          "ignore_above": 256
                        }
                      }
                    },
                    "Province": {
                      "type": "text",
                      "fields": {
                        "keyword": {
                          "type": "keyword",
                          "ignore_above": 256
                        }
                      }
                    },
                    "SerialNumber": {
                      "type": "text",
                      "fields": {
                        "keyword": {
                          "type": "keyword",
                          "ignore_above": 256
                        }
                      }
                    }
                  }
                },
                "IssuingCertificateURL": {
                  "type": "text",
                  "fields": {
                    "keyword": {
                      "type": "keyword",
                      "ignore_above": 256
                    }
                  }
                },
                "KeyUsage": {
                  "type": "long"
                },
                "MaxPathLen": {
                  "type": "long"
                },
                "MaxPathLenZero": {
                  "type": "boolean"
                },
                "NotAfter": {
                  "type": "date"
                },
                "NotBefore": {
                  "type": "date"
                },
                "OCSPServer": {
                  "type": "text",
                  "fields": {
                    "keyword": {
                      "type": "keyword",
                      "ignore_above": 256
                    }
                  }
                },
                "PermittedDNSDomainsCritical": {
                  "type": "boolean"
                },
                "PolicyIdentifiers": {
                  "type": "long"
                },
                "PublicKey": {
                  "properties": {
                    "E": {
                      "type": "text"
                    },
                    "N": {
                      "type": "text"
                    }
                  }
                },
                "PublicKeyAlgorithm": {
                  "type": "long"
                },
                "Raw": {
                  "type": "text",
                  "fields": {
                    "keyword": {
                      "type": "keyword",
                      "ignore_above": 256
                    }
                  }
                },
                "RawIssuer": {
                  "type": "text",
                  "fields": {
                    "keyword": {
                      "type": "keyword",
                      "ignore_above": 256
                    }
                  }
                },
                "RawSubject": {
                  "type": "text",
                  "fields": {
                    "keyword": {
                      "type": "keyword",
                      "ignore_above": 256
                    }
                  }
                },
                "RawSubjectPublicKeyInfo": {
                  "type": "text",
                  "fields": {
                    "keyword": {
                      "type": "keyword",
                      "ignore_above": 256
                    }
                  }
                },
                "RawTBSCertificate": {
                  "type": "text",
                  "fields": {
                    "keyword": {
                      "type": "keyword",
                      "ignore_above": 256
                    }
                  }
                },
                "SerialNumber": {
                  "type": "text"
                },
                "Signature": {
                  "type": "text",
                  "fields": {
                    "keyword": {
                      "type": "keyword",
                      "ignore_above": 256
                    }
                  }
                },
                "SignatureAlgorithm": {
                  "type": "long"
                },
                "Subject": {
                  "properties": {
                    "CommonName": {
                      "type": "text",
                      "fields": {
                        "keyword": {
                          "type": "keyword",
                          "ignore_above": 256
                        }
                      }
                    },
                    "Country": {
                      "type": "text",
                      "fields": {
                        "keyword": {
                          "type": "keyword",
                          "ignore_above": 256
                        }
                      }
                    },
                    "Locality": {
                      "type": "text",
                      "fields": {
                        "keyword": {
                          "type": "keyword",
                          "ignore_above": 256
                        }
                      }
                    },
                    "Names": {
                      "properties": {
                        "Type": {
                          "type": "long"
                        },
                        "Value": {
                          "type": "text",
                          "fields": {
                            "keyword": {
                              "type": "keyword",
                              "ignore_above": 256
                            }
                          }
                        }
                      }
                    },
                    "Organization": {
                      "type": "text",
                      "fields": {
                        "keyword": {
                          "type": "keyword",
                          "ignore_above": 256
                        }
                      }
                    },
                    "OrganizationalUnit": {
                      "type": "text",
                      "fields": {
                        "keyword": {
                          "type": "keyword",
                          "ignore_above": 256
                        }
                      }
                    },
                    "Province": {
                      "type": "text",
                      "fields": {
                        "keyword": {
                          "type": "keyword",
                          "ignore_above": 256
                        }
                      }
                    },
                    "SerialNumber": {
                      "type": "text",
                      "fields": {
                        "keyword": {
                          "type": "keyword",
                          "ignore_above": 256
                        }
                      }
                    }
                  }
                },
                "SubjectKeyId": {
                  "type": "text",
                  "fields": {
                    "keyword": {
                      "type": "keyword",
                      "ignore_above": 256
                    }
                  }
                },
                "Version": {
                  "type": "long"
                }
              }
            },
            "crawls": {
              "type": "nested",
              "fields": {
                "keyword": {
                  "type": "keyword",
                  "ignore_above": 256
                }
              }
            },
            "dateScanned": {
              "type": "date"
            },
            "f_name": {
              "type": "text",
              "fields": {
                "keyword": {
                  "type": "keyword",
                  "ignore_above": 256
                }
              }
            },
            "ftpBanner": {
              "type": "text",
              "fields": {
                "keyword": {
                  "type": "keyword",
                  "ignore_above": 256
                }
              }
            },
            "ftpDetected": {
              "type": "boolean"
            },
            "ftpFingerprint": {
              "type": "text",
              "fields": {
                "keyword": {
                  "type": "keyword",
                  "ignore_above": 256
                }
              }
            },
            "hiddenService": {
              "type": "text",
              "fields": {
                "keyword": {
                  "type": "keyword",
                  "ignore_above": 256
                }
              }
            },
            "identifierReport": {
              "properties": {
                "analyticsIDs": {
                  "type": "text",
                  "fields": {
                    "keyword": {
                      "type": "keyword",
                      "ignore_above": 256
                    }
                  }
                },
                "bitcoinAddresses": {
                  "type": "text",
                  "fields": {
                    "keyword": {
                      "type": "keyword",
                      "ignore_above": 256
                    }
                  }
                },
                "emailAddresses": {
                  "type": "text",
                  "fields": {
                    "keyword": {
                      "type": "keyword",
                      "ignore_above": 256
                    }
                  }
                },
                "exifImages": {
                  "properties": {
                    "exifTags": {
                      "properties": {
                        "name": {
                          "type": "text",
                          "fields": {
                            "keyword": {
                              "type": "keyword",
                              "ignore_above": 256
                            }
                          }
                        },
                        "value": {
                          "type": "text",
                          "fields": {
                            "keyword": {
                              "type": "keyword",
                              "ignore_above": 256
                            }
                          }
                        }
                      }
                    },
                    "location": {
                      "type": "text",
                      "fields": {
                        "keyword": {
                          "type": "keyword",
                          "ignore_above": 256
                        }
                      }
                    }
                  }
                },
                "foundApacheModStatus": {
                  "type": "boolean"
                },
                "linkedOnions": {
                  "type": "text",
                  "fields": {
                    "keyword": {
                      "type": "keyword",
                      "ignore_above": 256
                    }
                  }
                },
                "openDirectories": {
                  "type": "text",
                  "fields": {
                    "keyword": {
                      "type": "keyword",
                      "ignore_above": 256
                    }
                  }
                },
                "privateKeyDetected": {
                  "type": "boolean"
                },
                "serverVersion": {
                  "type": "text",
                  "fields": {
                    "keyword": {
                      "type": "keyword",
                      "ignore_above": 256
                    }
                  }
                }
              }
            },
            "ircDetected": {
              "type": "boolean"
            },
            "lastAction": {
              "type": "text",
              "fields": {
                "keyword": {
                  "type": "keyword",
                  "ignore_above": 256
                }
              }
            },
            "mongodbDetected": {
              "type": "boolean"
            },
            "online": {
              "type": "boolean"
            },
            "performedScans": {
              "type": "text",
              "fields": {
                "keyword": {
                  "type": "keyword",
                  "ignore_above": 256
                }
              }
            },
            "pgpKeys": {
              "properties": {
                "armoredKey": {
                  "type": "text",
                  "fields": {
                    "keyword": {
                      "type": "keyword",
                      "ignore_above": 256
                    }
                  }
                },
                "fingerprint": {
                  "type": "text",
                  "fields": {
                    "keyword": {
                      "type": "keyword",
                      "ignore_above": 256
                    }
                  }
                },
                "identity": {
                  "type": "text",
                  "fields": {
                    "keyword": {
                      "type": "keyword",
                      "ignore_above": 256
                    }
                  }
                }
              }
            },
            "ricochetDetected": {
              "type": "boolean"
            },
            "skynetDetected": {
              "type": "boolean"
            },
            "smtpBanner": {
              "type": "text",
              "fields": {
                "keyword": {
                  "type": "keyword",
                  "ignore_above": 256
                }
              }
            },
            "smtpDetected": {
              "type": "boolean"
            },
            "smtpFingerprint": {
              "type": "text",
              "fields": {
                "keyword": {
                  "type": "keyword",
                  "ignore_above": 256
                }
              }
            },
            "sshBanner": {
              "type": "text",
              "fields": {
                "keyword": {
                  "type": "keyword",
                  "ignore_above": 256
                }
              }
            },
            "sshDetected": {
              "type": "boolean"
            },
            "sshKey": {
              "type": "text",
              "fields": {
                "keyword": {
                  "type": "keyword",
                  "ignore_above": 256
                }
              }
            },
            "timedOut": {
              "type": "boolean"
            },
            "tlsDetected": {
              "type": "boolean"
            },
            "vncDetected": {
              "type": "boolean"
            },
            "webDetected": {
              "type": "boolean"
            },
            "xmppDetected": {
              "type": "boolean"
            }
          }
        },
        "screenshots": {
          "type": "nested",
          "properties": {
            "dateScreenshoted": {
              "type": "date"
            },
            "filename": {
              "type": "text",
              "fields": {
                "keyword": {
                  "type": "keyword",
                  "ignore_above": 256
                }
              }
            }
          }
        }
      }
    }
  }
}
        '''
        try:
            self.es = Elasticsearch([{
                'host':self.config['host'],
                'port':self.config['port']}])
            self.es.indices.create(
                    index=self.config['index'],
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
