# coding=utf-8
from gevent import monkey

monkey.patch_all()

import logging.config
import json
from munch import munchify
from simplejson import loads

logger = logging.getLogger(__name__)
from abc import ABCMeta, abstractmethod

from reports.brokers.databridge.utils import EdrDocument


class DataParser(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def processing_docs(self, tender_data):
        raise NotImplementedError

    @abstractmethod
    def process_items_and_move(self, response):
        raise NotImplementedError


class JSONDataParser(DataParser):
    def __init__(self):
        pass

    def processing_docs(self, tender_data):
        tender_id = tender_data['id']
        if 'awards' in tender_data and tender_data.get('awards'):
            for aw in tender_data['awards']:
                if aw and 'documents' in aw and aw.get('documents'):
                    for doc in aw['documents']:
                        doc_url = doc['url']
                        if 'bid_id' in aw and doc.get('documentType') == 'registerExtract':
                            bid_id = aw['bid_id']
                            logger.debug('Processing_docs data: {}'.format(EdrDocument(tender_id, bid_id, doc_url)))
                            return EdrDocument(tender_id, bid_id, doc_url)
                        else:
                            logger.debug(u'Tender {} award {} has no bidID'.format(tender_id, aw['id']))
                else:
                    logger.debug(u'Tender {} award {} has no documents'.format(tender_id, aw['id'] if aw else aw))
        else:
            logger.debug(u'Tender {} has no awards'.format(tender_id))

    def process_items_and_move(self, response):
        res = response.body_string()
        if type(res) == unicode:
            tender_json = munchify(loads(res))
        else:
            tender_json = munchify(loads(res.decode("utf-8")))
        try:
            tender_data = tender_json['data']
        except TypeError as e:
            logger.info("Could not parse tender_data. {}".format(e))
        except KeyError as e:
            logger.info("No data found. {}".format(e))
        else:
            edr_doc = self.processing_docs(tender_data)
            return tender_data, res, edr_doc
