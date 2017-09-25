# coding=utf-8
from gevent import monkey
monkey.patch_all()

import logging.config
import json
from munch import munchify
from simplejson import loads

logger = logging.getLogger(__name__)
from abc import ABCMeta, abstractmethod

from reports.brokers.databridge.constants import identification_scheme
from reports.brokers.databridge.utils import EdrDocument, is_code_invalid


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
                if aw and 'documents' in aw and aw.get('documents') and self.can_get_supplier_data(aw['suppliers'][0]):
                    identifier, scheme = self.get_supplier_data(aw["suppliers"][0])
                    for doc in aw['documents']:
                        doc_url = doc['url']
                        if 'bid_id' in aw and doc.get('documentType') == 'registerExtract':
                            bid_id = aw['bid_id']
                            logger.debug(u'Processing_docs data: {}_{}'.format(tender_id, bid_id))
                            return EdrDocument(tender_id, bid_id, identifier, scheme, doc_url)
                        else:
                            logger.debug(u'Tender {} award {} has no bidID'.format(tender_id, aw['id']))
                else:
                    logger.debug(u'Tender {} award {} has no documents'.format(tender_id, aw['id'] if aw else aw))
        else:
            logger.debug(u'Tender {} has no awards'.format(tender_id))

    def can_get_supplier_data(self, supplier):
        return (not is_code_invalid(supplier['identifier']['id'])) and self.should_process_award(supplier)

    def get_supplier_data(self, supplier):
        if self.can_get_supplier_data(supplier):
            return supplier["identifier"]["id"], supplier['identifier']['scheme']

    def should_process_award(self, supplier):
        return supplier['identifier']['scheme'] == identification_scheme

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
