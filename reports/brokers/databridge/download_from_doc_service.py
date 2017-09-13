# -*- coding: utf-8 -*-
from gevent import monkey

monkey.patch_all()


import re
import mysql.connector as mariadb
import gevent
import logging.config
import json

from gevent import spawn
from gevent.queue import Queue
from gevent.hub import LoopExit
from munch import munchify
from simplejson import loads
from datetime import datetime
from requests import RequestException

from reports.brokers.databridge.utils import journal_context
from reports.brokers.databridge.base_worker import BaseWorker

logger = logging.getLogger(__name__)


class DownloadFromDocServiceWorker(BaseWorker):
    """ Data Bridge """

    def __init__(self, services_not_available, doc_client, items_to_download_queue, edr_data_to_database):
        super(DownloadFromDocServiceWorker, self).__init__(services_not_available)
        self.items_to_download_queue = items_to_download_queue
        self.edr_data_to_database = edr_data_to_database
        self.doc_client = doc_client
        self.retry_items_to_download_queue = Queue(500)

    def get_item_from_doc_service(self):
        while not self.exit:
            self.temp_action()
            gevent.sleep()

    def temp_action(self):
        data = self.items_to_download_queue.peek()
        document = self.try_to_get_data(data)
        if document:
            res_data = (data.tender_id, data.bid_id, document)
            self.edr_data_to_database.put(res_data)
        else:
            self.retry_items_to_download_queue.put(data)
        self.items_to_download_queue.get()

    def try_to_get_data(self, data):
        try:
            return loads(self.doc_client.download(data.document_url).content)
        except RequestException as e:
            logger.info("Exception happened while trying to download: {}".format(e))
        except Exception as e:
            logger.info("Unknown exception happened. {}".format(e))

    def retry_get_item_from_doc_service(self):
        while not self.exit:
            self.retry_temp_action()
            gevent.sleep()

    def retry_temp_action(self):
        data = self.retry_items_to_download_queue.peek()
        document = self.try_to_get_data(data)
        res_data = (data.tender_id, data.bid_id, document)
        self.edr_data_to_database.put(res_data)

    def _start_jobs(self):
        return {'get_item_from_doc_service': spawn(self.get_item_from_doc_service),
                'retry_get_item_from_doc_service': spawn(self.retry_get_item_from_doc_service)}
