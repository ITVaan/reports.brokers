# coding=utf-8
from gevent import monkey

from reports.brokers.databridge.base_worker import BaseWorker

monkey.patch_all()

import mysql.connector as mariadb
from datetime import datetime
import gevent
import logging.config
import json
from gevent import spawn
from gevent.hub import LoopExit
from munch import munchify
from simplejson import loads
from reports.brokers.databridge.utils import journal_context, EdrDocument
from restkit.errors import ResourceError

logger = logging.getLogger(__name__)
from abc import ABCMeta, abstractmethod

from reports.brokers.databridge.utils import EdrDocument


class DataParser(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def processing_docs(self, tender_data):
        raise NotImplementedError

    @abstractmethod
    def process_items_and_move(self, response, tender_id):
        raise NotImplementedError


class JSONDataParser(DataParser):

    def __init__(self):
        pass

    def processing_docs(self, tender_data):
        tender_id = tender_data['id']
        if 'awards' in tender_data:
            for aw in tender_data['awards']:
                if 'documents' in aw:
                    for doc in aw['documents']:
                        doc_url = doc['url']
                        if 'bid_id' in aw:
                            bid_id = aw['bid_id']
                            logger.info('Processing_docs data: {}'.format(EdrDocument(tender_id, bid_id, doc_url)))
                            return EdrDocument(tender_id, bid_id, doc_url)
                        else:
                            logger.info('Tender {} award {} has no bidID'.format(tender_id, aw['id']))
                else:
                    logger.info('Tender {} award {} has no documents'.format(tender_id, aw['id']))
        else:
            logger.info('Tender {} has no awards'.format(tender_id))

    def process_items_and_move(self, response, tender_id):
        tender_json = munchify(loads(response.body_string().decode("utf-8")))
        tender_data = tender_json['data']
        self.processing_docs(tender_data)
        tender_str = json.dumps(tender_data)
        return tender_data, tender_str
