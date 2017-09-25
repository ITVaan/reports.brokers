# -*- coding: utf-8 -*-
from gevent import monkey
monkey.patch_all()

import gevent
import logging.config

from gevent import spawn
from gevent.queue import Queue
from yaml import load as load_yaml
from requests import RequestException

from reports.brokers.databridge.utils import EdrDocument, TendererData
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
        data = self.items_to_download_queue.get()
        doc = self.try_to_get_and_parse_data_from_doc_service(data)
        if doc is not None:
            self.edr_data_to_database.put(TendererData(data.identifier, data.scheme, doc[0], doc[1]))
            logger.info("Have put item into database: {}_{}. Queue size: {}".format(
                data.tender_id, data.bid_id, self.edr_data_to_database.qsize()))
        else:
            self.retry_items_to_download_queue.put(data)

    def try_to_get_and_parse_data_from_doc_service(self, data):
        # type: (EdrDocument) -> (None | (None|int, str))
        try:
            res = self.doc_client.download(data.document_url)
            edr_status, edr_date = self.parse_document(load_yaml(res))
            return edr_status, edr_date
        except RequestException as e:
            logger.info("Exception happened while trying to download: {}".format(e))
        except Exception as e:
            logger.info("Unknown exception happened. {}".format(e))

    def parse_document(self, edr_doc):
        # type: (dict)->(int, str)
        edr_status = None
        if edr_doc.get("errors") and edr_doc.get("errors").get("error") == "Couldn't find this code in EDR.":
            edr_status = 0
        elif edr_doc.get("data") and edr_doc.get("data").get("registrationStatus") == "registered":
            edr_status = 1
        edr_date = edr_doc.get("meta").get("sourceDate")
        return edr_status, edr_date

    def retry_get_item_from_doc_service(self):
        while not self.exit:
            self.retry_temp_action()
            gevent.sleep()

    def retry_temp_action(self):
        data = self.retry_items_to_download_queue.peek()
        doc = self.try_to_get_and_parse_data_from_doc_service(data)
        if doc:
            self.edr_data_to_database.put(TendererData(data.identifier, data.scheme, doc[0], doc[1]))
            self.retry_items_to_download_queue.get()
            logger.info("Have put item into database: {}_{}. Queue size: {}".format(
                data.tender_id, data.bid_id, self.retry_items_to_download_queue.qsize()))
        else:
            self.retry_items_to_download_queue.put(self.retry_items_to_download_queue.get())

    def _start_jobs(self):
        return {'get_item_from_doc_service': spawn(self.get_item_from_doc_service),
                'retry_get_item_from_doc_service': spawn(self.retry_get_item_from_doc_service)}
